function submitApplication(e) {
    e.preventDefault(); // You can ignore this; prevents the default form submission!

   const jobs = document.getElementsByName('job')
   let jobSelected = false
   for (let i = 0; i<jobs.length; i++){
        if(jobs[i].checked){
            alert("Thank you for applying to be a " + jobs[i].value + "!")
            jobSelected = true
            break
        }
   }
   if(!jobSelected){
    alert("Please select a Job!")
   }
}