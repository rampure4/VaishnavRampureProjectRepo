
let students = [];

fetch('https://cs571.org/api/s24/hw2/students', {
  headers: {
    "X-CS571-ID": CS571.getBadgerId()
  }
})
.then(response => response.json())
.then(data => {
  console.log(data); 
  students = data; 
  document.getElementById("num-results").innerText = `${students.length} student(s)`;
  buildStudents(students)
})
.catch(error => {
  console.error('There has been a problem with your fetch operation:', error);
});

function buildStudents(studs) {
  const nameHTML = document.getElementById("students");
  nameHTML.innerHTML = '';
  for(let student of studs) {
      const node = document.createElement('div');
      nameHTML.appendChild(node);
      node.className = 'col-12 col-sm-12 col-md-6 col-lg-4 col-xl-3 mb-4';

      const nameEl = document.createElement("h3");
      nameEl.textContent = `${student.name.first} ${student.name.last}`;
      node.appendChild(nameEl);

      const majorEl = document.createElement("b");
      majorEl.textContent = `Major: ${student.major}`;
      node.appendChild(majorEl);

      const creditsEl = document.createElement("p");
      creditsEl.textContent = `Credits: ${student.numCredits}`;
      node.appendChild(creditsEl);

      const fromWIEl = document.createElement("p");
      fromWIEl.textContent = `From Wisconsin: ${student.fromWisconsin ? 'Yes' : 'No'}`;
      node.appendChild(fromWIEl);

      const interestsEl = document.createElement("ul");
      student.interests.forEach(interest => {
          const interestItem = document.createElement("li");
          interestItem.textContent = interest;
          interestsEl.appendChild(interestItem);
      });
      node.appendChild(interestsEl);
  }
}

function handleSearch(e) {
	e?.preventDefault(); // You can ignore this; prevents the default form submission!
  const searchname = document.getElementById("search-name").value.trim().toLowerCase();
  const  searchmajor = document.getElementById("search-major").value.trim().toLowerCase();
  const searchinterest = document.getElementById("search-interest").value.trim().toLowerCase();
  const filterStudent = students.filter(student=>{
    const fullName = `${student.name.first} ${student.name.last}`.toLowerCase();
    const major = student.major.toLowerCase();
    const interests = student.interests.map(interest => interest.toLowerCase());
    const nameMatch = !searchname || fullName.includes(searchname);
    const majorMatch = !searchmajor || major.includes(searchmajor);
    const interestMatch = !searchinterest || interests.some(interest => interest.includes(searchinterest));
    return nameMatch && majorMatch && interestMatch
  }); 
  buildStudents(filterStudent);   
  document.getElementById("num-results").innerText = `${filterStudent.length} student(s)`;
}

document.getElementById("search-btn").addEventListener("click", handleSearch);