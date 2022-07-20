setInterval(() => {
  fetch("/progress")
  .then((res) => {
    res.text()
    .then((text) => {
      let prog = 60.0 - parseFloat(text);
      if (text == '' || prog <= 0.0)
        document.location.href = "/finished"
      let w = 100 - Math.floor((prog / 60) * 100)
      document.getElementById('bar').style.width = w + '%';
      document.getElementById('perc').innerHTML = w + '%';
    })
  })
  .catch((err) => console.log(err))
}, 1000)

