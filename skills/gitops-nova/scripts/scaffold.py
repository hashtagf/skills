#!/usr/bin/env python3
"""Scaffold an Argo CD GitOps repository with the known traps already handled.

    python3 scaffold.py --out ./acme-gitops --project acme \
      --repo git@github.com:acme/acme-gitops.git \
      --envs dev,uat,staging,prod --services api,worker

    python3 scaffold.py --out ./acme-gitops --project acme --repo <url> --minimal

What you get is a skeleton, not a finished repo: the structure, the AppProjects,
the appsets, and a shared service chart whose Helm traps (the `kindIs "bool"`
guard, per-component resource fallback, port-driven Service/probes/scrape, the
exempt-path `fail` guard) are already written. The values are yours to fill in.

Verify the chart renders before committing:

    helm template test charts/<project>-service \
      -f envs/dev/services/<svc>/values.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

NONPROD_ENVS = ("dev", "uat", "staging")


# --------------------------------------------------------------------- templates
# Placeholders are @@TOKEN@@ rather than str.format braces, because every one of
# these files is full of Go template `{{ }}`.

CHART_YAML = """apiVersion: v2
name: @@PROJECT@@-service
description: >-
  The one shared chart for every @@PROJECT@@ service. Per-service shape lives in
  values -- the components map (api + worker + any dev-only stand-in), env vars,
  ExternalSecret refs, and the route.
type: application
version: 0.1.0
appVersion: "0.1.0"
"""

HELPERS_TPL = """{{- define "@@PROJECT@@-service.name" -}}
{{ .Release.Name }}
{{- end }}

{{- define "@@PROJECT@@-service.labels" -}}
app.kubernetes.io/name: {{ include "@@PROJECT@@-service.name" . }}
app.kubernetes.io/managed-by: argocd
{{- end }}
"""

CHART_VALUES = """# Defaults for every @@PROJECT@@ service -- override per (service, env) in
# envs/<env>/services/<svc>/values.yaml.
#
# Secret VALUES never appear here or in any values file: only the path and the
# key names, synced in-cluster by External Secrets.

image:
  repository: ""      # registry path, e.g. registry.example.io/@@PROJECT@@/api
  tag: ""             # <env>-<sha> from CI, or the promoted release tag. NEVER `latest`.
  pullSecret: registry-pull   # kubernetes.io/dockerconfigjson Secret, per namespace

# One entry per running unit. Most services need only `app`.
#
# Three behaviours are DERIVED rather than flagged, so values cannot describe an
# impossible object:
#   port present        -> Service + scrape annotation. No port = a background
#                          worker: no Service, and nothing to scrape.
#   healthPath present  -> liveness + readiness probes. A component that serves no
#                          HTTP must omit it -- probes wired to a port it never
#                          opens are a guaranteed CrashLoopBackOff.
#   secrets: false      -> keep the synced Secret OUT of that container, for a
#                          component that is not the service (a dev-only mock).
#
# Per-component keys: replicas, env, resources, port, healthPath, readyPath,
# metrics {enabled, path}, secrets, image {repository, tag}, nodeSelector,
# tolerations, route {enabled, gatewayName, gatewayNamespace, hostnames}.
#
# The `app` component's Service keeps the bare release name; every other
# component is suffixed. That way adding a component can never rename the
# Service that other callers already dial.
components:
  app:
    replicas: 1
    port: 8080
    healthPath: /healthz    # STATIC -- "is this process wedged"
    readyPath: /readyz      # REAL   -- "can it serve right now"; pings dependencies
    env: {}

# A DEFAULT, not an empty map, and that is the point. `resources: {}` produces
# BestEffort QoS: those pods are evicted FIRST under node pressure, and with no
# memory limit one leak takes the whole node including other teams' pods.
#
# Size these from measurement, not intuition, and record the numbers in the
# per-service values when you override.
#
# NO cpu limit, deliberately: CPU is compressible, so the kernel throttles
# rather than kills -- a CPU limit turns "slow" into something indistinguishable
# from a hang, exactly under load. Memory is not compressible, so its limit does
# real work.
defaultResources:
  requests: {cpu: 10m, memory: 64Mi}
  limits:   {memory: 256Mi}

# Service-wide scheduling constraints; a component may override either.
# Empty by default so rendering is byte-identical for anything that does not use
# them. Prefer well-known labels (kubernetes.io/arch) over custom pool labels --
# the kubelet sets those without the autoscaler's help, so the selector keeps
# meaning the same thing if a pool is renamed or replaced.
nodeSelector: {}
tolerations: []

# Env shared by every component, merged UNDER per-component env.
env: {}

# ExternalSecret: key NAMES pulled from the secret manager at `path`.
secrets:
  enabled: false
  storeRef: @@STORE@@   # a store scoped to this project's paths, NOT the cluster-wide one
  path: ""              # e.g. @@PROJECT@@/dev/api
  keys: []              # e.g. [MONGO_URI, REDIS_PASSWORD]

# Caller-facing route. Default deny: a service is reachable in-cluster the moment
# it has a Service; a public route is a separate, deliberate act.
route:
  enabled: false
  gatewayName: @@GATEWAY@@
  gatewayNamespace: @@GATEWAY_NS@@
  hostnames: []
  # Which path prefixes the edge may forward AT ALL. Empty = catchall: every path
  # the process serves is published, including /metrics, any pprof handler, and
  # any ops plane it only ever expected on localhost. Set this to the real public
  # surface and everything unlisted gets a Gateway-level 404 -- the pod never sees
  # the request, no app change and no authz needed.
  paths: []
  # Paths that must skip edge auth (login, JWKS, provider callbacks). These render
  # into a separate, policy-free route, so each one MUST also be covered by a
  # `paths` prefix -- otherwise it reaches the pod around the allowlist. The
  # template refuses to render when that is violated; see httproute.yaml.
  jwtExemptPaths: []
  # Verify the token ONCE at the gateway and inject identity headers, so services
  # never verify tokens themselves. Only enable this on a service whose own gate
  # expects it -- and never publish such a service before the policy exists.
  jwt:
    enabled: false
    jwksURI: ""    # defaults to the in-cluster issuer; NEVER fetch through the CDN
    issuer: ""
    claimToHeaders:
      - {claim: sub,       header: X-User-Id}
      - {claim: tenant_id, header: X-Tenant-Id}
"""

DEPLOYMENT_TPL = """{{- range $name, $c := .Values.components }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "@@PROJECT@@-service.name" $ }}-{{ $name }}
  labels:
    {{- include "@@PROJECT@@-service.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ $name }}
spec:
  replicas: {{ $c.replicas | default 1 }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "@@PROJECT@@-service.name" $ }}
      app.kubernetes.io/component: {{ $name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ include "@@PROJECT@@-service.name" $ }}
        app.kubernetes.io/component: {{ $name }}
      {{- /* Scrape opt-in defaults to ON for any component that HAS a port, so a
             new service is monitored without a values change. A component with no
             port cannot be scraped -- that is a real gap for workers, and the fix
             is a port in the worker's own code, not a flag here.

             `default true $m.enabled` does NOT work: Helm's `default` treats false
             as empty and hands back the default, so an explicit `enabled: false`
             would be silently ignored. Hence the kindIs guard, which is also what
             the `secrets: false` opt-out below uses. */}}
      {{- $m := $c.metrics | default dict }}
      {{- $noScrape := and (kindIs "bool" $m.enabled) (not $m.enabled) }}
      {{- if and $c.port (not $noScrape) }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: {{ $c.port | quote }}
        prometheus.io/path: {{ $m.path | default "/metrics" | quote }}
      {{- end }}
    spec:
      {{- if $.Values.image.pullSecret }}
      imagePullSecrets:
        - name: {{ $.Values.image.pullSecret }}
      {{- end }}
      {{- /* Per-component first, then service-wide: pinning ONE component to an
             architecture is the whole point of a canary -- the app moves, its
             worker stays. `default` is safe for maps and lists; the bool trap
             above does not apply. */}}
      {{- with $c.nodeSelector | default $.Values.nodeSelector }}
      nodeSelector: {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with $c.tolerations | default $.Values.tolerations }}
      tolerations: {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: {{ $name }}
          {{- with $c.image }}
          image: "{{ .repository | default $.Values.image.repository }}:{{ .tag | default $.Values.image.tag }}"
          {{- else }}
          image: "{{ $.Values.image.repository }}:{{ $.Values.image.tag }}"
          {{- end }}
          {{- if $c.port }}
          ports:
            - containerPort: {{ $c.port }}
          {{- end }}
          env:
            {{- range $k, $v := $.Values.env }}
            - name: {{ $k }}
              value: {{ $v | quote }}
            {{- end }}
            {{- range $k, $v := $c.env }}
            - name: {{ $k }}
              value: {{ $v | quote }}
            {{- end }}
          {{- /* `secrets: false` keeps the synced Secret out of a component that
                 is not the service. envFrom is all-or-nothing per container, so
                 this is the only granularity available. */}}
          {{- $optedOut := and (kindIs "bool" $c.secrets) (not $c.secrets) }}
          {{- if and $.Values.secrets.enabled (not $optedOut) }}
          envFrom:
            - secretRef:
                name: {{ include "@@PROJECT@@-service.name" $ }}-secrets
          {{- end }}
          {{- if $c.healthPath }}
          livenessProbe:
            httpGet: {path: {{ $c.healthPath }}, port: {{ $c.port }}}
          readinessProbe:
            httpGet: {path: {{ $c.readyPath | default $c.healthPath }}, port: {{ $c.port }}}
          {{- end }}
          {{- /* Falls back PER COMPONENT. Without that, the default reaches only
                 `app` and every worker and sidecar ships BestEffort. A component
                 should have to opt OUT of resources, not remember to opt in. */}}
          resources: {{- ($c.resources | default $.Values.defaultResources) | toYaml | nindent 12 }}
---
{{- end }}
"""

SERVICE_TPL = """{{/*
One Service per component that listens on a port. Components without a port
(background workers) get none, by design.

The `app` component keeps the bare release name -- that is the name other
services already dial. Any other component is suffixed, so adding one can never
rename an existing Service.
*/}}
{{- range $name, $c := .Values.components }}
{{- if $c.port }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "@@PROJECT@@-service.name" $ }}{{ if ne $name "app" }}-{{ $name }}{{ end }}
  labels: {{- include "@@PROJECT@@-service.labels" $ | nindent 4 }}
spec:
  selector:
    app.kubernetes.io/name: {{ include "@@PROJECT@@-service.name" $ }}
    app.kubernetes.io/component: {{ $name }}
  ports:
    - port: 80
      targetPort: {{ $c.port }}
---
{{- end }}
{{- end }}
"""

EXTERNALSECRET_TPL = """{{- if .Values.secrets.enabled }}
{{- if not .Values.secrets.path }}
{{- fail "secrets.enabled is true but secrets.path is empty -- the ExternalSecret would resolve nothing and every pod would sit in CreateContainerConfigError." }}
{{- end }}
# Values live in the secret manager at {{ .Values.secrets.path }} -- never in git.
# Check which API version the RUNNING operator serves before changing this.
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {{ include "@@PROJECT@@-service.name" . }}
  labels: {{- include "@@PROJECT@@-service.labels" . | nindent 4 }}
spec:
  refreshInterval: 1m
  secretStoreRef:
    kind: ClusterSecretStore
    name: {{ .Values.secrets.storeRef }}
  target:
    name: {{ include "@@PROJECT@@-service.name" . }}-secrets
  data:
    {{- range .Values.secrets.keys }}
    - secretKey: {{ . }}
      remoteRef:
        key: {{ $.Values.secrets.path }}
        property: {{ . }}
    {{- end }}
{{- end }}
"""

HTTPROUTE_TPL = """{{- if .Values.route.enabled }}
{{- $jwt := .Values.route.jwt | default dict }}
{{- $jwtOn := default false $jwt.enabled }}
{{- if not .Values.route.hostnames }}
{{- fail "route.enabled is true but route.hostnames is empty -- the route would attach to the gateway listener with no host match." }}
{{- end }}
{{- /*
  route.paths and jwtExemptPaths interact, and getting it wrong is SILENT: the
  <name>-public route below carries NO policy and its own matches, so an exempt
  prefix that route.paths does not cover would be routed to the pod anyway,
  around the allowlist and unauthenticated. Refuse to render instead -- a Helm
  error is loud and lands on the author; a quietly re-opened path is found by
  whoever finds it first.

  "Covered" follows Gateway API PathPrefix semantics, which are SEGMENT-based,
  NOT string-based. `/api` does not match `/apiadmin`, so a plain hasPrefix would
  call `/apiadmin` covered by `/api` and wave through exactly the bypass this
  block exists to stop.

  An exempt entry EQUAL to an allowlisted prefix is rejected separately, because
  its effect is worse: two routes then carry the same prefix, one with the policy
  and one without, and Gateway API breaks that tie on route creation timestamp --
  so whether auth applies becomes nondeterministic.
*/ -}}
{{- if and $jwtOn .Values.route.paths .Values.route.jwtExemptPaths }}
{{- range $exempt := .Values.route.jwtExemptPaths }}
{{- $e := trimSuffix "/" $exempt }}
{{- $covered := false }}
{{- $equal := false }}
{{- range $allowed := $.Values.route.paths }}
{{- $p := trimSuffix "/" $allowed }}
{{- if eq $e $p }}
{{- $equal = true }}
{{- else if hasPrefix (printf "%s/" $p) $e }}
{{- $covered = true }}
{{- end }}
{{- end }}
{{- if $equal }}
{{- fail (printf "route.jwtExemptPaths entry %q is EQUAL to a route.paths prefix. Two routes would carry the same prefix -- one with the SecurityPolicy, one without -- and Gateway API breaks that tie on route creation timestamp, so whether auth applies would be nondeterministic. Make the exempt path more specific, or set route.jwt.enabled: false if the whole surface is meant to be public." $exempt) }}
{{- end }}
{{- if not $covered }}
{{- fail (printf "route.jwtExemptPaths entry %q is not covered by any route.paths prefix (%v) under Gateway API PathPrefix (segment) semantics. The policy-free %s-public route would carry it around the route.paths allowlist, unauthenticated. Add a covering prefix to route.paths, or drop the exempt path." $exempt $.Values.route.paths (include "@@PROJECT@@-service.name" $)) }}
{{- end }}
{{- end }}
{{- end }}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: {{ include "@@PROJECT@@-service.name" . }}
  labels: {{- include "@@PROJECT@@-service.labels" . | nindent 4 }}
spec:
  parentRefs:
    - name: {{ .Values.route.gatewayName }}
      namespace: {{ .Values.route.gatewayNamespace }}
  hostnames: {{- .Values.route.hostnames | toYaml | nindent 4 }}
  rules:
    - backendRefs:
        - name: {{ include "@@PROJECT@@-service.name" . }}
          port: 80
{{- if .Values.route.paths }}
      # With route.paths set this rule stops being a catchall: only these prefixes
      # are forwarded and everything else on the hostname 404s at the gateway.
      matches:
{{- range .Values.route.paths }}
        - path: {type: PathPrefix, value: {{ . | quote }}}
{{- end }}
{{- end }}
{{- if and $jwtOn .Values.route.jwtExemptPaths }}
---
# Policy-free twin for the exempt paths (login / JWKS / webhooks). Gateway API
# picks the most specific path match across routes, so these win over the
# protected route above; everything else stays behind the policy.
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: {{ include "@@PROJECT@@-service.name" . }}-public
  labels: {{- include "@@PROJECT@@-service.labels" . | nindent 4 }}
spec:
  parentRefs:
    - name: {{ .Values.route.gatewayName }}
      namespace: {{ .Values.route.gatewayNamespace }}
  hostnames: {{- .Values.route.hostnames | toYaml | nindent 4 }}
  rules:
    - matches:
        {{- range .Values.route.jwtExemptPaths }}
        - path: {type: PathPrefix, value: {{ . | quote }}}
        {{- end }}
      backendRefs:
        - name: {{ include "@@PROJECT@@-service.name" . }}
          port: 80
{{- end }}
{{- end }}
"""

COMPONENT_ROUTE_TPL = """{{/*
Per-COMPONENT route -- the sibling of httproute.yaml, which targets the release's
own Service only.

Why this exists: httproute.yaml hardcodes the backend to the `app` component's
Service (which keeps the bare release name). Every other component gets a
suffixed Service, so a route pointing at one is simply not expressible through
the release-level `route:` block.

Deliberately narrower: no JWT block and no exempt-path twin. A component route is
an operator or test surface, not a caller-facing API -- if one ever needs edge
auth it should graduate to being its own release with the full `route:`
treatment, rather than growing a second policy path here.

Renders nothing unless a component opts in.
*/}}
{{- range $name, $c := .Values.components }}
{{- $r := $c.route | default dict }}
{{- if and $c.port (default false $r.enabled) }}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: {{ include "@@PROJECT@@-service.name" $ }}-{{ $name }}
  labels: {{- include "@@PROJECT@@-service.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ $name }}
spec:
  parentRefs:
    - name: {{ $r.gatewayName | default $.Values.route.gatewayName }}
      namespace: {{ $r.gatewayNamespace | default $.Values.route.gatewayNamespace }}
  hostnames: {{- $r.hostnames | toYaml | nindent 4 }}
  rules:
    - backendRefs:
        # Matches service.yaml's naming: `app` keeps the bare release name,
        # everything else is suffixed. A component route never targets `app`.
        - name: {{ include "@@PROJECT@@-service.name" $ }}-{{ $name }}
          port: 80
---
{{- end }}
{{- end }}
"""

SECURITYPOLICY_TPL = """{{- $jwt := .Values.route.jwt | default dict }}
{{- if and .Values.route.enabled (default false $jwt.enabled) }}
# Verify the token ONCE at the gateway, inject the identity headers, and 401
# anything unsigned -- the pod never sees an unauthenticated request. Bound to
# the protected route only; the <name>-public route (exempt paths) deliberately
# carries no policy.
#
# This is the gateway.envoyproxy.io flavour. If your data plane is something
# else, replace the whole file -- the CONTRACT (verify at the edge, inject
# headers, fail closed) is what matters, not this CRD.
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: SecurityPolicy
metadata:
  name: {{ include "@@PROJECT@@-service.name" . }}-jwt
  labels: {{- include "@@PROJECT@@-service.labels" . | nindent 4 }}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: {{ include "@@PROJECT@@-service.name" . }}
  jwt:
    providers:
      - name: @@PROJECT@@-auth
        {{- if $jwt.issuer }}
        issuer: {{ $jwt.issuer | quote }}
        {{- end }}
        remoteJWKS:
          # In-cluster fetch -- NEVER through the CDN. Getting this wrong fails
          # closed and silently: the edge cannot fetch the key set, so EVERY
          # request 401s at the gateway and the pod logs nothing, because it
          # never sees a request.
          uri: {{ $jwt.jwksURI | default (printf "http://auth.%s.svc.cluster.local/.well-known/jwks.json" .Release.Namespace) | quote }}
        claimToHeaders: {{- $jwt.claimToHeaders | toYaml | nindent 10 }}
{{- end }}
"""

SERVICE_VALUES = """# @@SVC@@ @ @@ENV@@ -- @@OWNERSHIP@@
# Secret VALUES live in the secret manager at @@PROJECT@@/@@ENV@@/@@SVC@@ -- only
# key names appear here.
#
# Every non-obvious value below should carry its reason AND its exit condition:
# not what the line does, but what breaks if it changes, what was measured, and
# what has to become true before it can be deleted. Six months from now this file
# is the only surviving record of the decision.

image:
  repository: ""          # TODO: registry path
  tag: ""                 # TODO: a real built tag. CI overwrites this on push.
components:
  app:
    replicas: 1
    port: 8080
    healthPath: /healthz  # static liveness
    readyPath: /readyz    # real readiness -- pings dependencies
    env:
      LOG_LEVEL: @@LOGLEVEL@@
env: {}
secrets:
  enabled: false          # flip to true AFTER seeding @@PROJECT@@/@@ENV@@/@@SVC@@
  path: @@PROJECT@@/@@ENV@@/@@SVC@@
  keys: []
route:
  enabled: false          # default deny. When you enable it, set `paths` too --
  # an empty allowlist publishes every path the process serves, including any ops
  # plane it only ever expected on localhost.
"""

ROOT_APP = """# Apply once by hand after Argo CD is installed on the @@TIER@@ cluster:
#   kubectl apply -f bootstrap/@@TIER@@/root-app.yaml
# Everything else flows from this Application (app-of-apps).
#
# NOTE: prune here means deleting a file from apps/@@TIER@@/ deletes what it
# manages. That is intended for the Applications in that directory. It also
# reaches any RAW cluster-scoped manifest parked there -- keep that in mind
# before dropping a GatewayClass or a ClusterSecretStore in.
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-@@TIER@@
  namespace: argocd
spec:
  project: @@TIER@@
  source:
    repoURL: @@REPO@@
    targetRevision: main
    path: apps/@@TIER@@
    directory:
      recurse: true
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
@@SYNC@@
"""

ROOT_SYNC_NONPROD = """  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""

ROOT_SYNC_PROD = """  # No automated sync on prod: a reviewed merge and a deliberate sync are two
  # different acts of consent. Collapsing them makes every approving review a
  # deploy authorisation, which is not what a reviewer believes they are giving.
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
"""

PROJECT_NONPROD = """apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: nonprod
  namespace: argocd
spec:
  description: @@ENVLIST@@ -- dev-team self-serve
  # Exact URLs, not wildcards. Argo CD's glob matching against scp-form SSH URLs
  # is unreliable (the `:` is not a path separator), and the explicit list is the
  # tighter end state anyway.
  sourceRepos:
    - @@REPO@@
    - https://argoproj.github.io/argo-helm
    # add each upstream chart repo explicitly as you bring it up
  destinations:
@@DESTS@@    - server: https://kubernetes.default.svc
      namespace: argocd
  clusterResourceWhitelist:
    # TODO: narrow to the CRDs and ClusterRoles the platform charts actually
    # install. Wide open is a normal bring-up compromise; with nothing recorded
    # it becomes permanent by default.
    - group: "*"
      kind: "*"
"""

PROJECT_PROD = """apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: prod
  namespace: argocd
spec:
  description: prod -- locked; changes land only via reviewed PR (CODEOWNERS)
  sourceRepos:
    - @@REPO@@
    # upstream chart repos added one at a time, after they soak on nonprod.
    # No wildcards on prod, ever.
  destinations:
    - server: https://kubernetes.default.svc
      namespace: prod
    - server: https://kubernetes.default.svc
      namespace: argocd
  clusterResourceWhitelist:
    # TODO: narrow to what the platform charts install.
    - group: "*"
      kind: "*"
"""

SERVICES_APPSET = """# @@PROJECT@@ services x envs -- one Application per (service, env), all rendered
# from the single shared chart charts/@@PROJECT@@-service. Per-pair config lives in
# envs/<env>/services/<service>/values.yaml.
#
# The matrix is a CROSS PRODUCT: enabling an env requires a values file for EVERY
# service in the list. Park an env by commenting out its entry -- keep the values
# tree, so the work stays reviewable and re-enabling is one line.
#
# The generated name `<service>-<env>` is the handle RBAC globs use. Keep any
# policy that references it in lockstep with this template.
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: services-@@TIER@@
  namespace: argocd
spec:
  goTemplate: true
  generators:
    - matrix:
        generators:
          - list:
              elements:
@@ENVELEMS@@          - list:
              elements:
                # Onboard a service by adding it here AFTER its values.yaml
                # exists in every enabled env. The reverse order renders a red
                # app that reads like a platform fault and is really a missing
                # file.
@@SVCELEMS@@  template:
    metadata:
      name: "{{ .service }}-{{ .env }}"
    spec:
      project: @@TIER@@
      sources:
        # The chart comes from this repo; the values come from this repo too, via
        # a `ref` source. The ref source must have NO `path` -- give it one and
        # Argo CD renders that directory as well.
        - repoURL: @@REPO@@
          targetRevision: main
          ref: values
        - repoURL: @@REPO@@
          targetRevision: main
          path: charts/@@PROJECT@@-service
          helm:
            releaseName: "{{ .service }}"
            valueFiles:
              - "$values/envs/{{ .env }}/services/{{ .service }}/values.yaml"
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{ .env }}"
@@SYNC@@
"""

SERVICES_SYNC_NONPROD = """      syncPolicy:
        automated: {prune: true, selfHeal: true}
        syncOptions: [CreateNamespace=true]
"""

SERVICES_SYNC_PROD = """      syncPolicy:
        # No automated sync on prod -- a human presses sync after review.
        syncOptions: [CreateNamespace=true]
"""

PLATFORM_APPSET = """# Platform apps -- upstream Helm charts, once per cluster (not per env namespace).
# Versions are pinned here and bumped by PR (devops -- see CODEOWNERS).
#
# Chart version and the software version it ships are DIFFERENT numbers. Record
# both, or a bump PR cannot be reviewed without pulling the chart.
#
# Before adding anything here, check whether the cluster already runs it under
# another team. A second release of an operator fights the first over CRDs and
# webhooks, which is a much larger outage than the one you were avoiding.
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: platform-@@TIER@@
  namespace: argocd
spec:
  goTemplate: true
  generators:
    - list:
        elements: []
        # - name: gateway
        #   repoURL: oci://docker.io/envoyproxy/gateway-helm
        #   chart: gateway-helm
        #   version: "v1.8.2"        # ships Envoy Gateway v1.8.2
        #   namespace: @@GATEWAY_NS@@
  template:
    metadata:
      name: "{{ .name }}"
    spec:
      project: @@TIER@@
      source:
        repoURL: "{{ .repoURL }}"
        chart: "{{ .chart }}"
        targetRevision: "{{ .version }}"
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{ .namespace }}"
@@SYNC@@
"""

PLATFORM_SYNC_NONPROD = """      syncPolicy:
        automated: {prune: true, selfHeal: true}
        # ServerSideApply: charts bundling large CRDs blow the 256KB client-side
        # last-applied annotation limit, and it is also how a chart adopts CRDs
        # that were installed by hand at a lower version.
        syncOptions: [CreateNamespace=true, ServerSideApply=true]
"""

PLATFORM_SYNC_PROD = """      syncPolicy:
        # No automated sync on prod.
        syncOptions: [CreateNamespace=true, ServerSideApply=true]
"""

ARGOCD_SELF = """# Argo CD manages itself. Once the root app recurses apps/nonprod, this
# Application ADOPTS the release installed by hand, and every later change to
# Argo CD becomes a PR on bootstrap/argocd/values.yaml.
#
# Adoption works only because the chart version, the values file, and the release
# name all match the hand install. Any of the three drifting produces a permanent
# diff that looks like a bug and is really a bookkeeping error. The version is
# pinned in three places: the install command in bootstrap/argocd/README.md, the
# header of bootstrap/argocd/values.yaml, and targetRevision below.
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: argocd
  namespace: argocd
spec:
  project: nonprod
  sources:
    - repoURL: @@REPO@@
      targetRevision: main
      ref: values
    - repoURL: https://argoproj.github.io/argo-helm
      chart: argo-cd
      targetRevision: "@@ARGOCD_CHART@@"   # keep in lockstep with the helm install
      helm:
        releaseName: argocd
        valueFiles:
          - "$values/bootstrap/argocd/values.yaml"
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      selfHeal: true
      # Never prune Argo CD's own resources: if a bad render ever produces a
      # partial manifest set, pruning would delete the controller that would
      # otherwise let you fix it.
      prune: false
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true   # argo-cd CRDs exceed the client-side annotation limit
"""

ARGOCD_VALUES = """# Argo CD's own Helm values (argoproj/argo-helm), chart @@ARGOCD_CHART@@.
#
# Bootstrap is two-step -- see README.md in this directory:
#   1) helm install argocd argo/argo-cd -n argocd -f this-file --version @@ARGOCD_CHART@@
#   2) apps/nonprod/argocd-self.yaml makes Argo CD manage itself from here on.
# Keep this file and the pin in argocd-self.yaml in lockstep, or the self-app
# shows a permanent diff.
#
# Secrets are NEVER here: the private-repo credential is a Repository Secret
# created out of band. See README.md.

global:
  domain: argocd.example.com    # TODO: your hostname

configs:
  params:
    # TLS terminates at the edge, so run the API server HTTP-only behind it and
    # avoid double-TLS. This is correct ONLY when something in front terminates
    # TLS -- and with it set, route to the Service's port 80, not 443.
    server.insecure: true
  cm:
    url: https://argocd.example.com   # links and OIDC redirects are built from this
    exec.enabled: "false"             # the UI's pod-exec terminal
  rbac:
    # Deny by default. The chart's usual `role:readonly` hands every authenticated
    # account read over every application on this instance, including the ones
    # holding platform config. Grant explicitly instead, so a new account sees
    # nothing until someone decides what it should see.
    policy.default: ""
    policy.csv: |
      p, role:dev, applications,    get, nonprod/*, allow
      p, role:dev, logs,            get, nonprod/*, allow
      p, role:dev, projects,        get, nonprod,   allow
      p, role:dev, applicationsets, get, nonprod/*, allow

      # Sync + resource actions on SERVICE apps only. Project `nonprod` also holds
      # argocd itself, the root app, and the platform apps; `nonprod/*` would hand
      # those over too. The appset names every service app `<service>-<env>`, so
      # these globs select exactly the service apps -- keep them in lockstep with
      # that template.
      p, role:dev, applications, sync,     nonprod/*-dev, allow
      p, role:dev, applications, action/*, nonprod/*-dev, allow

      # Withheld on purpose (deny-by-default already covers these; named so the
      # intent survives the next edit):
      #   applications delete   -- an app is deleted by removing it from git
      #   applications update   -- editing live app spec bypasses git
      #   applications override -- syncing to an off-git revision
      #   repositories / clusters / accounts

      # g, alice, role:dev
"""

BOOTSTRAP_README = """# Bootstrap -- Argo CD

Argo CD installs the platform, but nothing installs Argo CD. Break the
chicken-and-egg in two steps: install by hand once, then let Argo CD adopt its
own release so every later change is a PR instead of a remembered `helm upgrade`.

Pin: chart **`argo-cd` @@ARGOCD_CHART@@**, repo
`https://argoproj.github.io/argo-helm`. Keep this in lockstep with
`values.yaml` (header) and `apps/nonprod/argocd-self.yaml` (`targetRevision`).

First, check whether this cluster already runs an Argo CD owned by another team.
Two releases fight over the same CRDs and webhooks. If one exists, becoming a
tenant of it (an AppProject plus an RBAC role) is almost always right.

## 1. Install by hand (once per cluster)

```bash
helm repo add argo https://argoproj.github.io/argo-helm && helm repo update
helm install argocd argo/argo-cd -n argocd --create-namespace \\
  --version @@ARGOCD_CHART@@ -f bootstrap/argocd/values.yaml
```

## 2. Give Argo CD the repo credential

Use a repo-scoped **read-only deploy key**, not a personal access token: a token
carries one human's whole account and dies when they leave.

```bash
ssh-keygen -t ed25519 -f argocd-deploykey -N "" -C "argocd-nonprod@@@PROJECT@@"

gh repo deploy-key add argocd-deploykey.pub \\
  --repo <org>/<repo> --title "argocd-nonprod-readonly"

# Prefer a file over an inline literal so the key never enters shell history.
kubectl -n argocd create secret generic gitops-repo \\
  --from-literal=type=git \\
  --from-literal=url=@@REPO@@ \\
  --from-file=sshPrivateKey=argocd-deploykey
kubectl -n argocd label secret gitops-repo argocd.argoproj.io/secret-type=repository

shred -u argocd-deploykey     # rm -P on macOS
```

The URL must match the manifests **character for character** -- Argo CD matches
repository credentials by exact string, so the `git@` and `https://` forms are
two different repositories to it.

## 3. Hand over to GitOps

```bash
kubectl apply -f bootstrap/nonprod/root-app.yaml
```

## 4. First login, and closing it

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \\
  -o jsonpath='{.data.password}' | base64 -d
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Delete `argocd-initial-admin-secret` after first login -- it is a static
credential that otherwise sits in etcd forever.

Before exposing the UI publicly, decide what guards it. The built-in admin plus
deny-by-default RBAC is a floor, and it is thin: the UI can sync anything the
account reaches, and it holds the repo credential. An identity-aware proxy in
front is the intended answer.

## Bring-up order

```
1. Argo CD                       (by hand)
2. Repo credential                -> without it every app is "repository not accessible"
3. Root app + AppProjects
4. Secret operator + its store    -> services with ExternalSecrets stay red until this exists
5. Gateway / ingress controller   -> routes resolve nowhere until the data plane is up
6. Identity service, if edge auth -> a policy with no JWKS behind it 401s EVERYTHING, silently
7. Observability                  -> before the fleet, so bring-up is visible
8. Services, ONE first, to green
```
"""

CODEOWNERS = """# Prod values: devops approval required -- dev teams self-serve @@ENVLIST@@.
# TODO: create the @@ORG@@/devops team, then enable branch protection requiring
# review from code owners. An unenforced CODEOWNERS reads as a control and is not one.
/envs/prod/     @@@ORG@@/devops

# Shared machinery affects every env.
/charts/        @@@ORG@@/devops
/apps/          @@@ORG@@/devops
/projects/      @@@ORG@@/devops
/bootstrap/     @@@ORG@@/devops
/platform/      @@@ORG@@/devops

# Observability: machinery gated, CONTENT deliberately self-serve.
# dashboards/ and alerts/ are left UNOWNED on purpose. A devops review on every
# dashboard reliably produces dashboards that live in the monitoring UI instead
# of in git -- the exact failure this repo exists to prevent. Do not "fix" this.
/observability/upstream/           @@@ORG@@/devops
/observability/chart/Chart.yaml    @@@ORG@@/devops
/observability/chart/values.yaml   @@@ORG@@/devops
/observability/chart/templates/    @@@ORG@@/devops
"""

REPO_README = """# @@PROJECT@@-gitops

Argo CD **app-of-apps** for @@PROJECT@@. Everything that runs **inside** the
clusters deploys from this repo. Cloud infrastructure (VPC, clusters, managed
databases) is Terraform and lives elsewhere -- never here.

## Layout

```
bootstrap/
  argocd/         Argo CD's own install values -- helm install once, then self-managed
  <tier>/         root Application per cluster (apply once by hand)
projects/         AppProject nonprod (broad) + prod (locked)
apps/
  <tier>/         app-of-apps leaves: ApplicationSets, Applications, raw manifests
charts/
  @@PROJECT@@-service/  the ONE shared service chart -- per-service shape lives in values
envs/
@@ENVTREE@@platform/         cluster-scoped objects, diffed but not applied
observability/    upstream pins (gated) + dashboards & alerts (self-serve)
```

## Rules

1. **Secrets are references, never values.** Values files carry a path and key
   names; the operator syncs the values in-cluster. Git is permanent and
   replicated -- a credential committed once is rotated, not removed.
2. **Pin every version.** Chart versions, image tags. Never `latest`, never
   `targetRevision: HEAD` on an upstream chart.
3. **Promote a digest, never a rebuild.** The artifact that soaked on staging is
   the artifact that ships. A rebuild from the same commit is a different
   artifact, which makes the soak meaningless.
4. **CI writes exactly one field** -- `image.tag` -- so `git log` keeps telling
   you which changes were decisions and which were robots.
5. **Routes are allowlists, not catchalls.** A catchall publishes every path the
   process serves, including the ops plane it expected on localhost.
6. **East-west uses the in-cluster address**, never the service's own public
   hostname.
7. **Every non-obvious value carries its reason and its exit condition.** Not
   what the line does -- what breaks if it changes, what was measured, and what
   has to be true before it can be deleted.

## Sync tiers

| Tier | Policy | Used for |
| --- | --- | --- |
| auto | `automated {prune, selfHeal}` | nonprod app workloads |
| manual | `syncOptions` only | prod |
| observe-only | no `automated:` block at all | cluster-scoped / shared objects |

`automated: {prune: false, selfHeal: false}` is **not** observe-only -- it still
applies git on every commit.

## Onboarding a service

```
1. envs/<env>/services/<svc>/values.yaml, in EVERY enabled env
2. seed the secret path
3. pin a real image tag
4. decide exposure (default: no route; a route needs a paths allowlist)
5. decide scrape (opt out WITH a comment naming what is missing)
6. add the generator entry -- last
7. watch it go green before onboarding the next
```
"""

GITIGNORE = """*.tgz
charts/*/charts/
.DS_Store
"""


def render(tpl: str, **kw: str) -> str:
    out = tpl
    for k, v in kw.items():
        out = out.replace(f"@@{k}@@", v)
    return out


def write(path: Path, content: str, force: bool, written: list[str], skipped: list[str]) -> None:
    if path.exists() and not force:
        skipped.append(str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    written.append(str(path))


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--out", required=True, help="target directory")
    ap.add_argument("--project", required=True, help="short project name (used in chart + paths)")
    ap.add_argument("--repo", required=True, help="git URL exactly as Argo CD will see it")
    ap.add_argument("--org", default=None, help="GitHub org for CODEOWNERS (default: from --repo)")
    ap.add_argument("--envs", default="dev,uat,staging,prod")
    ap.add_argument("--services", default="api")
    ap.add_argument("--minimal", action="store_true",
                    help="dev only, one service -- the smallest thing that can go green")
    ap.add_argument("--gateway", default="edge", help="Gateway resource name")
    ap.add_argument("--gateway-ns", default="envoy-gateway-system")
    ap.add_argument("--secret-store", default=None,
                    help="ClusterSecretStore name (default: <project>-secret-store)")
    ap.add_argument("--argocd-chart", default="10.1.4", help="argo-cd chart version to pin")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    project = args.project.strip().lower()
    if not project.replace("-", "").isalnum():
        sys.stderr.write("--project should be a short alphanumeric/dash name\n")
        return 2

    envs = ["dev"] if args.minimal else [e.strip() for e in args.envs.split(",") if e.strip()]
    services = (
        [args.services.split(",")[0].strip()]
        if args.minimal
        else [s.strip() for s in args.services.split(",") if s.strip()]
    )
    if not envs or not services:
        sys.stderr.write("need at least one env and one service\n")
        return 2

    nonprod = [e for e in envs if e != "prod"]
    has_prod = "prod" in envs
    store = args.secret_store or f"{project}-secret-store"

    org = args.org
    if not org:
        # git@github.com:acme/repo.git  |  https://github.com/acme/repo.git
        tail = args.repo.split(":")[-1].split("github.com/")[-1]
        org = tail.split("/")[0] if "/" in tail else "your-org"

    root = Path(args.out).expanduser().resolve()
    written: list[str] = []
    skipped: list[str] = []

    def emit(rel: str, content: str) -> None:
        write(root / rel, content, args.force, written, skipped)

    common = dict(
        PROJECT=project, REPO=args.repo, ORG=org, STORE=store,
        GATEWAY=args.gateway, GATEWAY_NS=args.gateway_ns,
        ARGOCD_CHART=args.argocd_chart, ENVLIST="/".join(nonprod),
    )

    # ---- chart
    cdir = f"charts/{project}-service"
    emit(f"{cdir}/Chart.yaml", render(CHART_YAML, **common))
    emit(f"{cdir}/values.yaml", render(CHART_VALUES, **common))
    emit(f"{cdir}/templates/_helpers.tpl", render(HELPERS_TPL, **common))
    emit(f"{cdir}/templates/deployment.yaml", render(DEPLOYMENT_TPL, **common))
    emit(f"{cdir}/templates/service.yaml", render(SERVICE_TPL, **common))
    emit(f"{cdir}/templates/externalsecret.yaml", render(EXTERNALSECRET_TPL, **common))
    emit(f"{cdir}/templates/httproute.yaml", render(HTTPROUTE_TPL, **common))
    emit(f"{cdir}/templates/component-httproute.yaml", render(COMPONENT_ROUTE_TPL, **common))
    emit(f"{cdir}/templates/securitypolicy.yaml", render(SECURITYPOLICY_TPL, **common))

    # ---- env values
    for env in envs:
        for svc in services:
            ownership = (
                "devops-gated (CODEOWNERS) -- promote the digest validated on staging"
                if env == "prod"
                else "dev-team self-serve: edit via PR, Argo CD auto-syncs"
            )
            emit(
                f"envs/{env}/services/{svc}/values.yaml",
                render(SERVICE_VALUES, SVC=svc, ENV=env, OWNERSHIP=ownership,
                       LOGLEVEL="info" if env == "prod" else "debug", **common),
            )

    # ---- projects
    dests = "".join(
        f'    - server: https://kubernetes.default.svc\n      namespace: {e}\n'
        for e in nonprod
    )
    emit("projects/nonprod.yaml", render(PROJECT_NONPROD, DESTS=dests, **common))
    if has_prod:
        emit("projects/prod.yaml", render(PROJECT_PROD, **common))

    # ---- bootstrap
    emit("bootstrap/argocd/values.yaml", render(ARGOCD_VALUES, **common))
    emit("bootstrap/argocd/README.md", render(BOOTSTRAP_README, **common))
    emit("bootstrap/nonprod/root-app.yaml",
         render(ROOT_APP, TIER="nonprod", SYNC=ROOT_SYNC_NONPROD, **common))
    if has_prod:
        emit("bootstrap/prod/root-app.yaml",
             render(ROOT_APP, TIER="prod", SYNC=ROOT_SYNC_PROD, **common))

    # ---- apps
    def env_elems(env_list: list[str]) -> str:
        # The first env is live; the rest are parked, because their secrets are
        # not seeded and no image is pinned yet -- an unparked broken env trains
        # the team to ignore red.
        out = []
        for i, e in enumerate(env_list):
            if i == 0:
                out.append(f"                - env: {e}\n")
            else:
                out.append(
                    f"                # Parked: seed {project}/{e}/<service> and pin an\n"
                    f"                # image tag in envs/{e}/... before enabling.\n"
                    f"                # - env: {e}\n"
                )
        return "".join(out)

    svc_elems = "".join(f"                - service: {s}\n" for s in services)

    emit("apps/nonprod/argocd-self.yaml", render(ARGOCD_SELF, **common))
    emit("apps/nonprod/services-appset.yaml", render(
        SERVICES_APPSET, TIER="nonprod", ENVELEMS=env_elems(nonprod),
        SVCELEMS=svc_elems, SYNC=SERVICES_SYNC_NONPROD, **common))
    emit("apps/nonprod/platform-appset.yaml", render(
        PLATFORM_APPSET, TIER="nonprod", SYNC=PLATFORM_SYNC_NONPROD, **common))
    if has_prod:
        emit("apps/prod/services-appset.yaml", render(
            SERVICES_APPSET, TIER="prod", ENVELEMS="                - env: prod\n",
            SVCELEMS=svc_elems, SYNC=SERVICES_SYNC_PROD, **common))
        emit("apps/prod/platform-appset.yaml", render(
            PLATFORM_APPSET, TIER="prod", SYNC=PLATFORM_SYNC_PROD, **common))

    # ---- repo-level
    envtree = "".join(
        f"  {e}/{'services/<svc>/values.yaml':<28}"
        + ("CODEOWNERS-gated\n" if e == "prod" else "dev self-serve via PR\n")
        for e in envs
    )
    emit("README.md", render(REPO_README, ENVTREE=envtree, **common))
    emit("CODEOWNERS", render(CODEOWNERS, **common))
    emit(".gitignore", GITIGNORE)
    (root / "platform").mkdir(parents=True, exist_ok=True)
    (root / "observability" / "chart" / "dashboards").mkdir(parents=True, exist_ok=True)
    (root / "observability" / "chart" / "alerts").mkdir(parents=True, exist_ok=True)
    (root / "observability" / "upstream").mkdir(parents=True, exist_ok=True)

    print(f"scaffolded {len(written)} files into {root}")
    for w in written:
        print(f"  + {Path(w).relative_to(root)}")
    if skipped:
        print(f"\n{len(skipped)} existing files left alone (use --force to overwrite):")
        for s in skipped:
            print(f"  = {Path(s).relative_to(root)}")

    first_env, first_svc = envs[0], services[0]
    print(f"""
Next:
  1. Verify the chart renders:
       helm template test {cdir} \\
         -f envs/{first_env}/services/{first_svc}/values.yaml
  2. Fill in image.repository / image.tag and the secret path in
     envs/{first_env}/services/{first_svc}/values.yaml
  3. Follow bootstrap/argocd/README.md to install Argo CD and hand over.
  4. Land ONE service green before adding a second.
  5. Audit before you grow: python3 audit.py {root}""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
