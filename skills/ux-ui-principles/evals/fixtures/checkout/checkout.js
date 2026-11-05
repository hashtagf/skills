document.getElementById("f").onsubmit=e=>{e.preventDefault();fetch("/pay",{method:"POST"}).then(()=>alert("Done"))} // no pending, no error, double-submit possible
