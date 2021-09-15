function upload(){
    document.getElementById('loading').hidden=false
    plant=document.getElementById('crop').value
    plant = plant.replace('/',' ')
    const myForm = document.getElementById('myForm')
    const file = document.getElementById('customFile')
    myForm.addEventListener('submit',e=>{
        e.preventDefault();
        const endpoint =' http://127.0.0.1:5000/upload'
        const formData = new FormData()
        formData.append('photo',file.files[0])
        formData.append('crop',plant)

        fetch(endpoint,{
            method:'post',
            body:formData
        })
        .then(response=>response.json())
        .then(data=>{
            document.getElementById('results').innerHTML=data['status']
            document.getElementById('loading').hidden=true
        })
        .catch(error=>{
            console.log(error)
        })
    })
    
}
window.onload=function(e){
   document.getElementById('loading').hidden=true
}