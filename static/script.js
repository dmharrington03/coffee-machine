setInterval(() => {
  fetch("/progress")
  .then((res) => console.log(res.text()))
  .catch((err) => console.log(err))
}, 5000)