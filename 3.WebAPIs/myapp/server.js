const express = require('express')
const app = express()
const port = 8080

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.post('/newstudent', (req, res, next) => {
  for (var i in req.body.students) {
    console.log(req.body.students[i].name + '\n');
  }
  res.status(201);
  res.end();
});

app.get("/students", (req, res, next) => {
    res.json({
      responseId: 1234,
      students: [
        { name: "Jordi", studentId: '12345678a' },
        { name: "Marta", studentId: '12345678b' }
      ]
    });
  });

/*
app.get('/students/:studentId', function (req, res) {
    res.send('Received request at /students with param studentId=' + req.params.studentId);
  });
*/


  app.listen(port, () => {
    console.log(`PTI HTTP Server listening at http://localhost:${port}`)
  })