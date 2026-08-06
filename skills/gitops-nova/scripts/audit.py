#!/usr/bin/env python3
"""Static audit of an Argo CD GitOps repository.

Checks what is mechanically decidable from the files alone. It cannot see your
cluster, your IAM policies, or the inside of an image, so a clean run means the
obvious checks passed -- not that the repo is sound. The judgment half lives in
references/review.md.

    python3 audit.py <repo>                     human-readable, ordered by severity
    python3 audit.py <repo> --format json       for CI
    python3 audit.py <repo> --fail-on high      exit 1 -- use as a merge gate
    python3 audit.py <repo> --only RT,SEC       run one or more check families

Requires PyYAML.
"""

from __future__ import annotations

import argparse
import fnmatch
import itertools
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "audit.py needs PyYAML.\n"
        "  pip install pyyaml   (or: python3 -m pip install --user pyyaml)\n"
    )
    raise SystemExit(2)


SEVERITIES = ("high", "medium", "low")

# Kinds that exist outside any namespace. Deleting one of these on a shared
# cluster reaches every tenant, which is why `prune` on a path holding them is
# treated as a high finding rather than a style note.
CLUSTER_SCOPED = {
    "APIService",
    "ClusterIssuer",
    "ClusterPolicy",
    "ClusterRole",
    "ClusterRoleBinding",
    "ClusterSecretStore",
    "ClusterWorkflowTemplate",
    "CSIDriver",
    "CustomResourceDefinition",
    "EC2NodeClass",
    "GatewayClass",
    "IngressClass",
    "MutatingWebhookConfiguration",
    "Namespace",
    "NodePool",
    "PersistentVolume",
    "PriorityClass",
    "RuntimeClass",
    "StorageClass",
    "ValidatingWebhookConfiguration",
}

SECRETISH_KEY = re.compile(
    r"(?i)(password|passwd|secret|token|apikey|api_key|privatekey|private_key|"
    r"credential|access_key|accesskey|client_secret)"
)
# Keys whose value is legitimately a *name* or a *path*, not a credential.
REFERENCE_KEY = re.compile(
    r"(?i)^(secretname|existingsecret|secretkey|storeref|pullsecret|imagepullsecret|"
    r"secretref|passwordkey|tokenkey|keys?|path|name|type|kind|.*keyref)$"
)
URI_WITH_CREDS = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://([^/\s:@]+):([^/\s@]+)@")
PEM_MARKER = re.compile(r"-----BEGIN [A-Z ]*(PRIVATE KEY|CERTIFICATE)")
# Values that are indirections, not credentials: env/file references, Helm and
# Go template expressions, and shell-style substitution.
INDIRECTION = re.compile(r"\$__(env|file|vault)\{|\$\{|\$\(|\{\{")
# Obvious stand-ins. Flagging these trains people to ignore the check.
PLACEHOLDER = re.compile(
    r"(?i)^(pass(word)?|secret|token|changeme|redacted|x{3,}|\*{3,}|"
    r"your[-_]?\w*|<[^>]+>|\.{3,})$"
)
MUTABLE_REVISIONS = {"", "head", "*", "latest", "main", "master", "develop"}
TEMPLATE_TOKEN = re.compile(r"\{\{\s*\.?([\w.]+)\s*\}\}")
GO_TEMPLATE = re.compile(r"\{\{")


@dataclass
class Finding:
    code: str
    severity: str
    title: str
    path: str
    line: int | None = None
    detail: str = ""
    fix: str = ""

    def sort_key(self) -> tuple:
        return (SEVERITIES.index(self.severity), self.code, self.path, self.line or 0)


@dataclass
class Repo:
    root: Path
    # (relpath, doc) for every YAML document that parsed as a mapping
    docs: list[tuple[str, dict]] = field(default_factory=list)
    # relpath -> raw text, for line lookup and regex-only checks
    text: dict[str, str] = field(default_factory=dict)
    # relpath -> parsed values mapping, for files that are Helm values
    values: dict[str, dict] = field(default_factory=dict)
    unparsed: list[str] = field(default_factory=list)

    def rel(self, p: Path) -> str:
        return str(p.relative_to(self.root))


# --------------------------------------------------------------------------- load


def is_helm_template(rel: str) -> bool:
    parts = Path(rel).parts
    return "templates" in parts


def looks_like_values(rel: str, doc: dict) -> bool:
    """Helm values files have no apiVersion/kind and live in a values-ish place."""
    if "apiVersion" in doc or "kind" in doc:
        return False
    name = Path(rel).name
    return name in ("values.yaml", "values.yml") or "/envs/" in "/" + rel


def load_repo(root: Path) -> Repo:
    repo = Repo(root=root)
    skip_dirs = {".git", ".github", "node_modules", ".venv", "__pycache__"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if not fn.endswith((".yaml", ".yml")):
                continue
            p = Path(dirpath) / fn
            rel = repo.rel(p)
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            repo.text[rel] = raw

            if is_helm_template(rel) and GO_TEMPLATE.search(raw):
                # Helm templates are not YAML. Raw-text checks only.
                continue
            try:
                docs = list(yaml.safe_load_all(raw))
            except yaml.YAMLError:
                repo.unparsed.append(rel)
                continue
            for doc in docs:
                if not isinstance(doc, dict):
                    continue
                repo.docs.append((rel, doc))
                if looks_like_values(rel, doc):
                    repo.values[rel] = doc
    return repo


def approx_line(text: str, *keys: str) -> int | None:
    """Best-effort line number for a key. Reported as approximate on purpose --
    exact positions would need a line-tracking loader, and the file name plus a
    nearby line is enough to find a key in a values file."""
    for key in reversed(keys):
        if not key:
            continue
        pat = re.compile(rf"^\s*-?\s*{re.escape(key)}\s*:", re.MULTILINE)
        m = pat.search(text)
        if m:
            return text[: m.start()].count("\n") + 1
    return None


def walk_scalars(node: Any, trail: tuple = ()) -> Iterable[tuple[tuple, Any]]:
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_scalars(v, trail + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_scalars(v, trail + (f"[{i}]",))
    else:
        yield trail, node


def get(node: Any, *path: str, default=None):
    cur = node
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def sources_of(spec: dict) -> list[dict]:
    out = []
    if isinstance(spec.get("source"), dict):
        out.append(spec["source"])
    if isinstance(spec.get("sources"), list):
        out.extend(s for s in spec["sources"] if isinstance(s, dict))
    return out


def app_specs(repo: Repo) -> Iterable[tuple[str, dict, dict]]:
    """Yield (relpath, doc, spec) for Applications and ApplicationSet templates."""
    for rel, doc in repo.docs:
        kind = doc.get("kind")
        if kind == "Application":
            spec = doc.get("spec")
            if isinstance(spec, dict):
                yield rel, doc, spec
        elif kind == "ApplicationSet":
            spec = get(doc, "spec", "template", "spec")
            if isinstance(spec, dict):
                yield rel, doc, spec


# ------------------------------------------------------------------------- checks


def _credential_uri(value: str) -> str | None:
    """Return a redacted `user:***@host` when the string really carries a credential.

    Config blobs (an Alloy river file, a Grafana provisioning block) arrive as one
    multi-line scalar, and their *comments* frequently spell out the very pattern
    this check looks for. Matching those trains people to ignore the finding, so
    comment lines are skipped and obvious placeholders are ignored.
    """
    for line in value.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "*", "--")):
            continue
        for m in URI_WITH_CREDS.finditer(line):
            user, secret = m.group(1), m.group(2)
            if PLACEHOLDER.match(secret) or INDIRECTION.search(secret):
                continue
            return f"{user}:***@"
    return None


def check_secrets(repo: Repo, out: list[Finding]) -> None:
    for rel, doc in repo.docs:
        text = repo.text.get(rel, "")

        if doc.get("kind") == "Secret":
            for field_name in ("data", "stringData"):
                blob = doc.get(field_name)
                if isinstance(blob, dict) and blob:
                    out.append(Finding(
                        "SEC001", "high",
                        f"Secret manifest with non-empty {field_name} committed to git",
                        rel, approx_line(text, field_name),
                        f"Keys: {', '.join(sorted(blob))}. Git is replicated and permanent -- "
                        "`git rm` does not unpublish, and rewriting history does not reach clones.",
                        "Move the values into your secret manager and render an ExternalSecret "
                        "carrying only the path and the key names (references/secrets.md).",
                    ))

        for trail, value in walk_scalars(doc):
            if not isinstance(value, str) or not value:
                continue
            key = trail[-1] if trail else ""
            where = ".".join(trail)

            hit = _credential_uri(value)
            if hit:
                out.append(Finding(
                    "SEC002", "high", "Connection URI with embedded credentials in git",
                    rel, approx_line(text, key),
                    f"`{where}` holds a URI with a user:password pair ({hit}).",
                    "Store the whole URI in the secret manager; keep only the path and key name here.",
                ))
                continue

            if PEM_MARKER.search(value):
                out.append(Finding(
                    "SEC003", "high", "PEM private key or certificate in git",
                    rel, approx_line(text, key),
                    f"`{where}` contains a PEM block.",
                    "Move it to the secret manager and reference it by key name.",
                ))
                continue

            if (
                SECRETISH_KEY.search(key)
                and not REFERENCE_KEY.match(key)
                and not INDIRECTION.search(value)
                and not PLACEHOLDER.match(value)
            ):
                # A k8s object name (lowercase, digits, dots, dashes) is a reference,
                # not a credential -- `pullSecret: harbor-pull` must not fire here.
                looks_like_name = re.fullmatch(r"[a-z0-9][a-z0-9._/-]*", value) is not None
                high_entropy = (
                    len(value) >= 16
                    and re.search(r"[A-Z]", value)
                    and re.search(r"[a-z0-9]", value)
                ) or re.search(r"[+=/]{2,}", value)
                if not looks_like_name and (high_entropy or len(value) >= 24):
                    out.append(Finding(
                        "SEC004", "high", "Value under a credential-shaped key looks like a secret",
                        rel, approx_line(text, key),
                        f"`{where}` = {value[:12]}... ({len(value)} chars). If this is a literal "
                        "credential it is now permanent in history.",
                        "If it is a reference (a name or a path), ignore this. If it is a value, "
                        "rotate it and move it to the secret manager.",
                    ))


def check_pins(repo: Repo, out: list[Finding]) -> None:
    parked = parked_tokens(repo)
    for rel, doc, spec in app_specs(repo):
        text = repo.text.get(rel, "")
        name = get(doc, "metadata", "name", default="?")
        for src in sources_of(spec):
            rev = str(src.get("targetRevision", "") or "")
            if TEMPLATE_TOKEN.search(rev):
                continue
            if src.get("chart"):
                if rev.strip().lower() in MUTABLE_REVISIONS:
                    out.append(Finding(
                        "PIN001", "high", "Upstream Helm chart is not pinned",
                        rel, approx_line(text, "targetRevision"),
                        f"App `{name}` sources chart `{src['chart']}` at "
                        f"targetRevision `{rev or '<unset>'}`.",
                        "Pin an exact chart version, and note in a comment which software "
                        "version that chart ships -- they are different numbers.",
                    ))
                elif re.match(r"^[~^>=<]", rev.strip()):
                    out.append(Finding(
                        "PIN002", "medium", "Helm chart pinned to a range, not a version",
                        rel, approx_line(text, "targetRevision"),
                        f"App `{name}` uses `{rev}` -- someone else's release becomes your "
                        "unreviewed deploy.",
                        "Pin an exact version and bump it by PR.",
                    ))
            elif rev.strip().lower() in ("head", ""):
                out.append(Finding(
                    "PIN003", "medium", "Git source tracks a mutable/unset revision",
                    rel, approx_line(text, "targetRevision"),
                    f"App `{name}` uses targetRevision `{rev or '<unset>'}`.",
                    "Track a named branch you control (`main`) or a tag.",
                ))

    for rel, vals in repo.values.items():
        text = repo.text.get(rel, "")
        image = vals.get("image")
        if not isinstance(image, dict):
            continue
        chart_default = _is_chart_default(rel)
        tag = image.get("tag")
        repo_field = image.get("repository")
        if tag in (None, "") and not chart_default and not (set(Path(rel).parts) & parked):
            out.append(Finding(
                "PIN004", "medium", "Image tag is empty",
                rel, approx_line(text, "tag"),
                "An empty tag renders `repository:` and the pod fails as InvalidImageName. "
                "This is expected for an env that is deliberately parked.",
                "Pin a real built tag, or say in a comment that this env is parked and why.",
            ))
        elif str(tag).strip().lower() in ("latest", "main", "master"):
            out.append(Finding(
                "PIN005", "high", "Image tag is mutable",
                rel, approx_line(text, "tag"),
                f"`image.tag: {tag}` -- what ran yesterday and what runs now are not the same "
                "artifact, and rollback has no target.",
                "Pin an immutable tag (`<env>-<sha>`) or a digest.",
            ))
        if repo_field in (None, "") and tag:
            out.append(Finding(
                "PIN006", "medium", "Image repository is empty but a tag is set",
                rel, approx_line(text, "repository"), "", "Set image.repository.",
            ))


def check_sync(repo: Repo, out: list[Finding]) -> None:
    # Which directories hold cluster-scoped objects, and which are app-of-apps
    # leaf directories (they also hold Applications / ApplicationSets)?
    cluster_dirs: dict[str, set[str]] = {}
    appofapps_dirs: set[str] = set()
    for rel, doc in repo.docs:
        kind = doc.get("kind")
        parent = str(Path(rel).parent).replace("\\", "/")
        if kind in CLUSTER_SCOPED:
            cluster_dirs.setdefault(parent, set()).add(kind)
        elif kind in ("Application", "ApplicationSet"):
            appofapps_dirs.add(parent)

    for rel, doc, spec in app_specs(repo):
        text = repo.text.get(rel, "")
        name = get(doc, "metadata", "name", default="?")
        automated = get(spec, "syncPolicy", "automated")
        if automated is None:
            continue
        prune = bool(get(spec, "syncPolicy", "automated", "prune", default=False))
        for src in sources_of(spec):
            path = str(src.get("path", "") or "").strip("/")
            if not path or TEMPLATE_TOKEN.search(path):
                continue
            kinds = cluster_dirs.get(path)
            if not kinds:
                continue
            if prune and path in appofapps_dirs:
                # The root app must prune -- that is how removing a leaf removes what it
                # manages. The finding is the raw cluster-scoped manifests parked in the
                # same directory, which silently inherit that behaviour.
                out.append(Finding(
                    "SYNC001", "medium",
                    "Raw cluster-scoped manifests inherit the root app's prune",
                    rel, approx_line(text, "prune", "automated"),
                    f"App `{name}` prunes `{path}/`, an app-of-apps directory that also holds "
                    f"{', '.join(sorted(kinds))} as raw manifests. Deleting or renaming one of "
                    "those files deletes a cluster-scoped object that reaches every tenant.",
                    "Fine if deliberate -- note it in the manifest. If the object should outlive "
                    "a file move, give it its own Application at the observe-only tier.",
                ))
            elif prune:
                out.append(Finding(
                    "SYNC001", "high", "prune enabled on a path holding cluster-scoped objects",
                    rel, approx_line(text, "prune", "automated"),
                    f"App `{name}` prunes `{path}/`, which holds {', '.join(sorted(kinds))}. "
                    "A moved directory or a bad generator deletes objects that reach every "
                    "tenant of the cluster.",
                    "Drop to the observe-only tier: remove the whole `automated:` block "
                    "(references/sync-policy.md).",
                ))
            elif path in appofapps_dirs:
                continue
            else:
                out.append(Finding(
                    "SYNC002", "medium",
                    "automated sync on cluster-scoped objects is not observe-only",
                    rel, approx_line(text, "automated"),
                    f"App `{name}` manages {', '.join(sorted(kinds))} under `{path}/`. Even with "
                    "prune and selfHeal false, git still applies on every commit -- and a "
                    "requirement change on these objects is usually a fleet-wide replacement.",
                    "Remove the `automated:` block entirely so the app renders a diff instead "
                    "of applying one.",
                ))

        if name and str(name).strip() == "argocd" and prune:
            out.append(Finding(
                "SYNC003", "high", "Argo CD's self-managed Application has prune enabled",
                rel, approx_line(text, "prune"),
                "A bad render could delete the controller that would let you fix it.",
                "Set prune: false on the self-app; keep selfHeal: true.",
            ))


def check_projects(repo: Repo, out: list[Finding]) -> None:
    projects: dict[str, dict] = {}
    for rel, doc in repo.docs:
        if doc.get("kind") != "AppProject":
            continue
        name = get(doc, "metadata", "name")
        if not name:
            continue
        pspec = doc.get("spec") or {}
        projects[name] = {"rel": rel, "spec": pspec}
        text = repo.text.get(rel, "")
        repos = pspec.get("sourceRepos") or []
        if any(str(r).strip() == "*" for r in repos):
            out.append(Finding(
                "PROJ001", "high", "AppProject allows any source repository",
                rel, approx_line(text, "sourceRepos"),
                f"Project `{name}` has `sourceRepos: ['*']` -- any chart from anywhere may be "
                "deployed into its namespaces.",
                "List the repositories explicitly. Argo CD's glob matching is also unreliable "
                "against scp-form SSH URLs, so exact URLs are both tighter and more predictable.",
            ))
        crw = pspec.get("clusterResourceWhitelist") or []
        wide = any(
            str(e.get("group")) == "*" and str(e.get("kind")) == "*"
            for e in crw if isinstance(e, dict)
        )
        if wide and not re.search(r"(?i)todo|narrow|bring-?up", text):
            out.append(Finding(
                "PROJ002", "low", "clusterResourceWhitelist is wide open with no stated plan",
                rel, approx_line(text, "clusterResourceWhitelist"),
                f"Project `{name}` permits every cluster-scoped kind. That is a normal bring-up "
                "compromise; with nothing recorded it becomes permanent by default.",
                "Add a TODO naming what it should narrow to once the platform charts are in.",
            ))
        if not (pspec.get("destinations") or []):
            out.append(Finding(
                "PROJ003", "medium", "AppProject has no destination allowlist",
                rel, approx_line(text, "spec"),
                f"Project `{name}` bounds no namespace, so a template rendering an unintended "
                "destination lands silently instead of failing at the project boundary.",
                "List the namespaces this project may deploy into.",
            ))

    for rel, doc, spec in app_specs(repo):
        proj = spec.get("project")
        if not proj or proj not in projects or TEMPLATE_TOKEN.search(str(proj)):
            continue
        allowed = [str(r) for r in (projects[proj]["spec"].get("sourceRepos") or [])]
        if not allowed:
            continue
        text = repo.text.get(rel, "")
        name = get(doc, "metadata", "name", default="?")
        for src in sources_of(spec):
            url = str(src.get("repoURL", "") or "")
            # Any Go-template expression (including `{{ default "x" .repoURL }}`)
            # resolves per generated Application, so it cannot be checked statically.
            if not url or GO_TEMPLATE.search(url):
                continue
            if not any(url == a or fnmatch.fnmatch(url, a) for a in allowed):
                out.append(Finding(
                    "PROJ004", "medium", "Application sources a repo its AppProject forbids",
                    rel, approx_line(text, "repoURL"),
                    f"App `{name}` (project `{proj}`) uses `{url}`, which is not in that "
                    "project's sourceRepos. Argo CD refuses this at sync time.",
                    f"Add the URL to projects/{proj}, character for character.",
                ))


def _covers(prefix: str, path: str) -> str | None:
    """Gateway API PathPrefix semantics: SEGMENT-based, not string-based.
    `/api` covers `/api/v2` but not `/apiadmin`."""
    p = prefix.rstrip("/")
    e = path.rstrip("/")
    if p == e:
        return "equal"
    if p == "" or e.startswith(p + "/"):
        return "covered"
    return None


AUTH_POLICY_KIND = re.compile(
    r"^\s*kind:\s*(SecurityPolicy|AuthorizationPolicy|RequestAuthentication|AuthPolicy)\s*$",
    re.MULTILINE,
)


def values_to_chart(repo: Repo) -> dict[str, str]:
    """Map each values file to the chart directory that consumes it.

    Built from the Applications and ApplicationSets themselves rather than
    guessed from the path, because the whole point of the shared-chart layout is
    that `envs/dev/services/payment/values.yaml` feeds `charts/nova-service`, not
    a chart named `payment`.
    """
    mapping: dict[str, str] = {}
    for rel, doc, spec in app_specs(repo):
        srcs = sources_of(spec)
        chart_paths = [
            str(s.get("path", "")).strip("/")
            for s in srcs
            if s.get("path") and not GO_TEMPLATE.search(str(s.get("path")))
        ]
        if not chart_paths:
            continue
        chart = chart_paths[0]
        contexts = (
            _generator_contexts(doc.get("spec") or {})
            if doc.get("kind") == "ApplicationSet"
            else [{}]
        )
        for src in srcs:
            for vf in (get(src, "helm", "valueFiles") or []):
                if not isinstance(vf, str):
                    continue
                for ctx in contexts or [{}]:
                    rendered = TEMPLATE_TOKEN.sub(
                        lambda m: str(ctx.get(m.group(1).lstrip("."), m.group(0))), vf
                    )
                    if GO_TEMPLATE.search(rendered):
                        continue
                    mapping[_values_ref(rendered)] = chart
    return mapping


def charts_with_auth_template(repo: Repo) -> set[str]:
    """Chart directories shipping their own auth-policy template.

    A chart can bind an edge policy to its route without the release-level
    `route.jwt` block knowing anything about it -- an analytics chart with its
    own basic-auth policy is the common case. Without this, every such route
    reads as unauthenticated, which is the kind of false positive that teaches
    people to stop reading the output.
    """
    charts: set[str] = set()
    for template_rel, text in repo.text.items():
        parts = Path(template_rel).parts
        if "templates" not in parts or not AUTH_POLICY_KIND.search(text):
            continue
        idx = parts.index("templates")
        if idx:
            charts.add("/".join(parts[:idx]))
    return charts


def _is_chart_default(rel: str) -> bool:
    """`charts/<x>/values.yaml` states defaults that per-env values override, so its
    route is not by itself a deployed route. Any other values file is real."""
    parts = Path(rel).parts
    return len(parts) >= 3 and parts[0] == "charts" and parts[-1] in ("values.yaml", "values.yml")


def check_routes(repo: Repo, out: list[Finding]) -> None:
    hostnames: dict[str, list[str]] = {}
    chart_of = values_to_chart(repo)
    auth_charts = charts_with_auth_template(repo)

    def _chart_has_auth(values_rel: str) -> bool:
        chart = chart_of.get(values_rel.replace("\\", "/"))
        return bool(chart and chart in auth_charts)

    for rel, vals in repo.values.items():
        text = repo.text.get(rel, "")
        chart_default = _is_chart_default(rel)
        blocks: list[tuple[str, dict]] = []
        route = vals.get("route")
        if isinstance(route, dict):
            blocks.append(("route", route))
        comps = vals.get("components")
        if isinstance(comps, dict):
            for cname, c in comps.items():
                if isinstance(c, dict) and isinstance(c.get("route"), dict):
                    blocks.append((f"components.{cname}.route", c["route"]))

        for where, route in blocks:
            if not route.get("enabled"):
                continue
            hosts = route.get("hostnames") or []
            if not chart_default:
                for h in hosts:
                    hostnames.setdefault(str(h), []).append(rel)

            if not hosts and not chart_default:
                out.append(Finding(
                    "RT001", "medium", "Route enabled with no hostnames",
                    rel, approx_line(text, "hostnames", "enabled"),
                    f"`{where}` is enabled but declares no hostname, so it attaches to the "
                    "gateway's listener without a host match.",
                    "Declare the hostname, or disable the route.",
                ))

            paths = route.get("paths") or []
            _jwt = route.get("jwt")
            jwt = _jwt if isinstance(_jwt, dict) else {}
            jwt_on = bool(jwt.get("enabled"))
            exempt = route.get("jwtExemptPaths") or []

            if not paths and chart_default:
                out.append(Finding(
                    "RT002", "low", "Chart default enables a catchall route",
                    rel, approx_line(text, "paths", "enabled"),
                    f"`{where}` defaults to enabled with no path allowlist, so every consumer "
                    "that does not override it publishes its whole surface.",
                    "Default `route.enabled: false`, and require `paths` when it is turned on.",
                ))
            elif not paths:
                out.append(Finding(
                    "RT002", "high", "Public route is a catchall",
                    rel, approx_line(text, "paths", "hostnames"),
                    f"`{where}` forwards EVERY path on {', '.join(map(str, hosts)) or 'its host'} "
                    "-- including /metrics, any pprof handler, and any ops or admin plane the "
                    "process serves on the same listener."
                    # Only ASSERT "unauthenticated" when nothing could be authenticating it.
                    # A chart shipping its own policy template is invisible in these values, so
                    # asserting it there is the kind of wrong that discredits the whole report --
                    # but dropping the point entirely loses the signal, so hedge instead.
                    + ("" if jwt_on else
                       (f" No `route.jwt` is set either; chart `{chart_of.get(rel)}` does ship an "
                        "auth-policy template, so check whether it binds to this route before "
                        "treating the surface as protected."
                        if _chart_has_auth(rel) else
                        " There is also no edge authentication declared on it.")),
                    "Set `paths:` to the real public surface. Everything unlisted then 404s at "
                    "the gateway and the pod never sees it (references/exposure.md).",
                ))

            # Only when RT002 did not already fire: a catchall route with no auth is
            # one problem to fix, not two rows describing the same file.
            elif not jwt_on and hosts and not chart_default:
                chart = chart_of.get(rel.replace("\\", "/"))
                if _chart_has_auth(rel):
                    out.append(Finding(
                        "RT003", "low", "Route has no `route.jwt`, but its chart ships an auth policy",
                        rel, approx_line(text, "jwt", "hostnames"),
                        f"`{where}` publishes {', '.join(map(str, hosts))} with no `route.jwt` "
                        f"block, but chart `{chart}` carries its own auth-policy template. "
                        "Whether this route is protected depends on that template's render "
                        "condition, which cannot be read from values.",
                        "Read the chart's policy template and confirm it binds to this route. If "
                        "it does, this is fine -- say so in a comment here so the next reader "
                        "does not have to repeat the trace.",
                    ))
                else:
                    out.append(Finding(
                        "RT003", "low", "Route is allowlisted but has no edge authentication",
                        rel, approx_line(text, "jwt", "hostnames"),
                        f"`{where}` publishes {', '.join(map(str, hosts))} with no edge policy. "
                        "That is fine if the service authenticates itself -- and full "
                        "impersonation if it only checks that identity headers are present.",
                        "Confirm which model this service uses. If it trusts injected headers, an "
                        "edge policy is required before the route is public.",
                    ))

            # Exempt paths only mean anything when a policy exists to be exempt FROM.
            if exempt and not jwt_on and not chart_default:
                out.append(Finding(
                    "RT007", "medium", "Exempt paths declared but edge auth is off",
                    rel, approx_line(text, "jwtExemptPaths"),
                    f"`{where}` lists jwtExemptPaths {list(exempt)} while route.jwt.enabled is "
                    "not set. The list is inert -- nothing is being exempted, because nothing is "
                    "enforced. Worse, the values now READ as though the route is protected with "
                    "a carve-out, which is how a reviewer concludes auth is handled.",
                    "Either set route.jwt.enabled: true (after confirming the identity service is "
                    "live and serving JWKS), or drop the exempt list and state plainly that this "
                    "route is unauthenticated.",
                ))

            if jwt_on and paths and exempt:
                for e in exempt:
                    verdicts = {_covers(str(p), str(e)) for p in paths}
                    if "equal" in verdicts:
                        out.append(Finding(
                            "RT004", "high", "Exempt path equals an allowlisted prefix",
                            rel, approx_line(text, "jwtExemptPaths"),
                            f"`{e}` appears both in route.paths and route.jwtExemptPaths. Two "
                            "routes then carry the same prefix -- one with the policy, one "
                            "without -- and Gateway API breaks that tie on route creation "
                            "timestamp. Whether auth applies is nondeterministic.",
                            "Make the exempt path more specific than the allowlisted prefix, or "
                            "set jwt.enabled: false if the whole surface is meant to be public.",
                        ))
                    elif "covered" not in verdicts:
                        out.append(Finding(
                            "RT005", "high", "Exempt path bypasses the route allowlist",
                            rel, approx_line(text, "jwtExemptPaths"),
                            f"`{e}` is not covered by any entry in route.paths ({paths}) under "
                            "segment-based PathPrefix semantics. The policy-free twin route "
                            "carries it around the allowlist, unauthenticated.",
                            "Add a covering prefix to route.paths, or drop the exempt path. "
                            "Better: make the chart `fail` on this (references/service-chart.md).",
                        ))

    for host, files in hostnames.items():
        if len(files) > 1:
            out.append(Finding(
                "RT006", "medium", "Hostname declared by more than one route",
                files[0], approx_line(repo.text.get(files[0], ""), "hostnames"),
                f"`{host}` is claimed in: {', '.join(sorted(set(files)))}. Which backend wins "
                "depends on match specificity and route creation time.",
                "Give each service its own hostname, or make the path matches disjoint and say "
                "so in a comment.",
            ))

    # East-west traffic sent through the repo's own public hostnames.
    own_hosts = set(hostnames)
    if own_hosts:
        for rel, vals in repo.values.items():
            text = repo.text.get(rel, "")
            for trail, value in walk_scalars(vals):
                if not isinstance(value, str) or "://" not in value:
                    continue
                if "hostnames" in trail:
                    continue
                m = re.match(r"https?://([^/\s:]+)", value)
                if m and m.group(1) in own_hosts:
                    out.append(Finding(
                        "EW001", "medium", "East-west call uses this repo's own public hostname",
                        rel, approx_line(text, *(trail[-1:] or ())),
                        f"`{'.'.join(trail)}` = {value}. This hairpins pod -> NAT -> CDN -> "
                        "edge -> back into the same cluster: slower, billed on both legs, and "
                        "it starts returning 401 the day edge auth is enabled on that host.",
                        "Use the in-cluster address (http://<service>[/prefix]). Keep the "
                        "version/group prefix in the base URL.",
                    ))


def check_chart_values(repo: Repo, out: list[Finding]) -> None:
    for rel, vals in repo.values.items():
        text = repo.text.get(rel, "")
        comps = vals.get("components")
        if not isinstance(comps, dict):
            continue
        for cname, c in comps.items():
            if not isinstance(c, dict):
                continue
            port = c.get("port")
            if c.get("healthPath") and not port:
                out.append(Finding(
                    "CHART001", "high", "Component has a probe path but no port",
                    rel, approx_line(text, "healthPath"),
                    f"Component `{cname}` sets healthPath with no port. Probes are wired to a "
                    "port it never opens, which is a guaranteed CrashLoopBackOff that reads "
                    "like an application bug.",
                    "Drop healthPath for a component that serves no HTTP, or give it a port.",
                ))
            if c.get("readyPath") and c.get("healthPath") and c["readyPath"] == c["healthPath"]:
                out.append(Finding(
                    "CHART002", "low", "Liveness and readiness use the same path",
                    rel, approx_line(text, "readyPath"),
                    f"Component `{cname}` points both probes at `{c['readyPath']}`. If that "
                    "handler checks dependencies, the first broker or database blip CrashLoops "
                    "every replica instead of just removing them from the endpoints.",
                    "Liveness static, readiness real. If the service only serves one path, say "
                    "so in a comment so the next reader knows it was considered.",
                ))
            res = c.get("resources")
            if isinstance(res, dict):
                if not res:
                    out.append(Finding(
                        "CHART003", "medium", "Component pinned to empty resources",
                        rel, approx_line(text, "resources"),
                        f"Component `{cname}` sets `resources: {{}}`, which produces BestEffort "
                        "QoS -- evicted first under node pressure, and no memory limit means one "
                        "leak takes the node.",
                        "Remove the key to inherit the chart default, or set real values.",
                    ))
                cpu_limit = get(res, "limits", "cpu")
                if cpu_limit:
                    out.append(Finding(
                        "CHART004", "low", "CPU limit set",
                        rel, approx_line(text, "limits"),
                        f"Component `{cname}` limits CPU to {cpu_limit}. CPU is compressible, so "
                        "the kernel throttles rather than kills -- a CPU limit turns 'slow' into "
                        "something indistinguishable from a hang, under load.",
                        "Keep the request, drop the limit, unless you are deliberately capping a "
                        "noisy neighbour and have said so.",
                    ))

    for rel, vals in repo.values.items():
        if "/charts/" not in "/" + rel or Path(rel).name not in ("values.yaml", "values.yml"):
            continue
        if not isinstance(vals.get("components"), dict):
            continue
        has_default = any(
            k in vals for k in ("defaultResources", "resources")
        )
        if not has_default:
            out.append(Finding(
                "CHART005", "medium", "Shared chart has no default resources",
                rel, approx_line(repo.text.get(rel, ""), "components"),
                "Without a default that falls back PER COMPONENT, every worker and sidecar ships "
                "BestEffort. Measured on a real fleet: 13 of 15 containers, because the default "
                "reached only the primary component.",
                "Add `defaultResources` and fall back to it in the template with "
                "`($c.resources | default $.Values.defaultResources)`.",
            ))


PARKED_ELEMENT = re.compile(r"^\s*#\s*-\s*(\w+)\s*:\s*([\w.-]+)\s*$", re.MULTILINE)


def parked_tokens(repo: Repo) -> set[str]:
    """Values that appear as COMMENTED-OUT generator elements.

    Parking an environment by commenting out its list entry -- while keeping the
    values tree -- is the documented way to say "not yet, and here is why". Reading
    those comments is what lets the audit tell a parked env from a forgotten one,
    which is the whole distinction GEN002 and PIN004 are trying to draw.
    """
    parked: set[str] = set()
    for rel, doc in repo.docs:
        if doc.get("kind") != "ApplicationSet":
            continue
        for match in PARKED_ELEMENT.finditer(repo.text.get(rel, "")):
            parked.add(match.group(2))
    return parked


def _values_ref(vf: str) -> str:
    """`$values/envs/dev/services/x/values.yaml` -> `envs/dev/services/x/values.yaml`."""
    out = vf.split("/", 1)[1] if vf.startswith("$values/") else vf
    return out.lstrip("/").replace("\\", "/")


def check_generators(repo: Repo, out: list[Finding]) -> None:
    produced: set[str] = set()
    parked = parked_tokens(repo)

    # A values file can also be claimed by a plain Application (anything the
    # appsets cannot express: a StatefulSet chart, a dev-only workload). Count
    # those first, or GEN002 reports them as orphans.
    for rel, doc, spec in app_specs(repo):
        if doc.get("kind") != "Application":
            continue
        for src in sources_of(spec):
            for vf in (get(src, "helm", "valueFiles") or []):
                if isinstance(vf, str) and not GO_TEMPLATE.search(vf):
                    produced.add(_values_ref(vf))

    for rel, doc in repo.docs:
        if doc.get("kind") != "ApplicationSet":
            continue
        text = repo.text.get(rel, "")
        name = get(doc, "metadata", "name", default="?")
        spec = doc.get("spec") or {}
        contexts = _generator_contexts(spec)
        tmpl = get(spec, "template", "spec") or {}
        value_files = [
            vf
            for src in sources_of(tmpl)
            for vf in (get(src, "helm", "valueFiles") or [])
            if isinstance(vf, str)
        ]
        if not contexts or not value_files:
            continue
        for ctx in contexts:
            for vf in value_files:
                rendered = TEMPLATE_TOKEN.sub(
                    lambda m: str(ctx.get(m.group(1).lstrip("."), m.group(0))), vf
                )
                if GO_TEMPLATE.search(rendered):
                    continue
                rel_target = _values_ref(rendered)
                produced.add(rel_target)
                if not (repo.root / rel_target).is_file():
                    out.append(Finding(
                        "GEN001", "high", "Generator entry points at a values file that does not exist",
                        rel, approx_line(text, "elements"),
                        f"ApplicationSet `{name}` generates {ctx} -> `{rel_target}`, which is "
                        "missing. The Application renders red and reads like a platform fault.",
                        "Create the values file first, then add the generator entry. Order "
                        "matters (references/promotion.md).",
                    ))

    if produced:
        for rel in repo.values:
            if not rel.replace("\\", "/").startswith("envs/"):
                continue
            if Path(rel).name not in ("values.yaml", "values.yml"):
                continue
            if rel.replace("\\", "/") in produced:
                continue
            text = repo.text.get(rel, "")
            if re.search(r"(?i)park|disabled|not yet|deliberate|pending", text):
                continue
            # Or the generator itself parks it: `# - env: uat` with a reason.
            if set(Path(rel).parts) & parked:
                continue
            out.append(Finding(
                "GEN002", "low", "Values file is not referenced by any generator",
                rel, 1,
                "Nothing deploys this. That is fine for a parked environment and indistinguishable "
                "from a forgotten one when nothing says which it is.",
                "Add a comment saying it is parked and what has to be true to enable it, or "
                "delete it.",
            ))


def _generator_contexts(spec: dict) -> list[dict]:
    contexts: list[dict] = []
    for gen in spec.get("generators") or []:
        if not isinstance(gen, dict):
            continue
        if isinstance(gen.get("list"), dict):
            contexts.extend(
                e for e in (gen["list"].get("elements") or []) if isinstance(e, dict)
            )
        elif isinstance(gen.get("matrix"), dict):
            subs = gen["matrix"].get("generators") or []
            lists = [
                [e for e in (g["list"].get("elements") or []) if isinstance(e, dict)]
                for g in subs
                if isinstance(g, dict) and isinstance(g.get("list"), dict)
            ]
            if lists and len(lists) == len(subs):
                for combo in itertools.product(*lists):
                    merged: dict = {}
                    for part in combo:
                        merged.update(part)
                    contexts.append(merged)
    return contexts


def check_ownership(repo: Repo, out: list[Finding]) -> None:
    candidates = [repo.root / "CODEOWNERS", repo.root / ".github" / "CODEOWNERS",
                  repo.root / "docs" / "CODEOWNERS"]
    owners_file = next((p for p in candidates if p.is_file()), None)
    if owners_file is None:
        out.append(Finding(
            "OWN001", "medium", "No CODEOWNERS file",
            ".", None,
            "Nothing distinguishes a prod values change from a dev one at review time.",
            "Gate machinery (charts/, apps/, projects/, bootstrap/) and envs/prod/; leave "
            "dashboards, alerts and nonprod values unowned on purpose (references/layout.md).",
        ))
        return

    body = owners_file.read_text(encoding="utf-8", errors="replace")
    want = {
        "/charts/": "the shared chart affects every service in every env",
        "/apps/": "the app-of-apps leaves decide what exists and at which sync tier",
        "/projects/": "AppProjects are the blast-radius boundary",
        "/bootstrap/": "this is how Argo CD itself is configured",
        "/envs/prod/": "production values",
    }
    present_dirs = {d for d in want if (repo.root / d.strip("/")).is_dir()}
    missing = [d for d in sorted(present_dirs) if d not in body]
    if missing:
        out.append(Finding(
            "OWN002", "medium", "CODEOWNERS does not cover shared machinery",
            repo.rel(owners_file), None,
            "Unowned: " + ", ".join(f"{d} ({want[d]})" for d in missing),
            "Add a line per path. CODEOWNERS also does nothing without branch protection "
            "requiring code-owner review -- verify that separately.",
        ))


# One pass per family of checks. `check_routes` emits both RT* and EW* findings,
# so --only filters the resulting codes rather than the passes -- otherwise
# `--only EW` would have to know that it lives inside the route pass.
CHECKS = {
    "secrets": check_secrets,
    "pins": check_pins,
    "sync": check_sync,
    "projects": check_projects,
    "routes": check_routes,
    "chart": check_chart_values,
    "generators": check_generators,
    "ownership": check_ownership,
}

FAMILIES = ("SEC", "PIN", "SYNC", "PROJ", "RT", "EW", "CHART", "GEN", "OWN")


# ------------------------------------------------------------------------- output


def render_text(repo: Repo, findings: list[Finding]) -> str:
    lines: list[str] = []
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITIES}
    lines.append(f"GitOps audit — {repo.root}")
    lines.append(
        f"{len(repo.docs)} manifests · {len(repo.values)} values files · "
        f"{counts['high']} high · {counts['medium']} medium · {counts['low']} low"
    )
    if repo.unparsed:
        lines.append(f"unparsed YAML (skipped): {', '.join(repo.unparsed[:5])}"
                     + (" …" if len(repo.unparsed) > 5 else ""))
    lines.append("")

    if not findings:
        lines.append("No findings from the mechanical checks.")
    for sev in SEVERITIES:
        group = [f for f in findings if f.severity == sev]
        if not group:
            continue
        lines.append(f"── {sev.upper()} ({len(group)}) " + "─" * max(0, 50 - len(sev)))
        for f in group:
            loc = f"{f.path}:{f.line}" if f.line else f.path
            lines.append(f"  [{f.code}] {f.title}")
            lines.append(f"      {loc}")
            if f.detail:
                for chunk in _wrap(f.detail, 92):
                    lines.append(f"      {chunk}")
            if f.fix:
                for i, chunk in enumerate(_wrap(f.fix, 92)):
                    lines.append(f"      {'fix: ' if i == 0 else '     '}{chunk}")
            lines.append("")
    lines.append("Not checked from files alone: the live cluster, IAM scopes behind role ARNs,")
    lines.append("image contents, whether secret paths exist, branch protection, and what the")
    lines.append("application code actually serves. See references/review.md for those.")
    return "\n".join(lines)


def _wrap(text: str, width: int) -> list[str]:
    words, out, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        out.append(cur)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="path to the GitOps repository")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--fail-on", choices=SEVERITIES, default=None,
                    help="exit 1 if any finding at this severity or above is present")
    ap.add_argument("--only", default=None,
                    help="comma-separated finding families: " + ",".join(FAMILIES))
    args = ap.parse_args()

    root = Path(args.repo).expanduser().resolve()
    if not root.is_dir():
        sys.stderr.write(f"not a directory: {root}\n")
        return 2

    selected = None
    if args.only:
        selected = {s.strip().upper() for s in args.only.split(",") if s.strip()}
        unknown = selected - set(FAMILIES)
        if unknown:
            sys.stderr.write(
                f"unknown family: {', '.join(sorted(unknown))}\n"
                f"known: {', '.join(FAMILIES)}\n"
            )
            return 2

    repo = load_repo(root)

    findings: list[Finding] = []
    for family, fn in CHECKS.items():
        try:
            fn(repo, findings)
        except Exception as exc:  # a broken repo must not break the audit
            findings.append(Finding(
                "AUDIT999", "low", f"the {family} check failed to run",
                ".", None, f"{type(exc).__name__}: {exc}",
                "This is an audit bug, not a repo finding. Every other check still ran.",
            ))

    if selected is not None:
        findings = [
            f for f in findings
            if f.code.startswith("AUDIT")
            or any(f.code.startswith(fam) and not f.code[len(fam)].isalpha()
                   for fam in selected if len(f.code) > len(fam))
        ]

    findings.sort(key=lambda f: f.sort_key())

    if args.format == "json":
        print(json.dumps({
            "repo": str(root),
            "manifests": len(repo.docs),
            "values_files": len(repo.values),
            "unparsed": repo.unparsed,
            "counts": {s: sum(1 for f in findings if f.severity == s) for s in SEVERITIES},
            "findings": [asdict(f) for f in findings],
        }, indent=2))
    else:
        print(render_text(repo, findings))

    if args.fail_on:
        threshold = SEVERITIES.index(args.fail_on)
        if any(SEVERITIES.index(f.severity) <= threshold for f in findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
