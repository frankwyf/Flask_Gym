const form = document.getElementById('form');
const username = document.getElementById('username');
const password = document.getElementById('password');
const button = document.getElementById('toggle');
const body = document.querySelector('body');
const signup = document.querySelector('.signup');
const remember = document.querySelector('.remember');
const manager = document.querySelector('.manager');
const forget = document.querySelector('.forget');
const container = document.querySelector('.container');
let success = 0;//mark whether the register is successful

$("#remember").change(function(){
     alert("Don't remember login status? Some functions will be disabled!");
})

form.addEventListener('submit', e => {
    e.preventDefault();
    LoginCheck();//run validation functions every time we submit
})

setInterval(function() {
var e = document.createEvent("MouseEvents");
e.initEvent("click", true, false);
document.getElementById("toggle").dispatchEvent(e);
}, 3000);

button.onclick = function () {
    button.classList.toggle('dark');
    body.classList.toggle('dark');
    form.classList.toggle('dark');
    signup.classList.toggle('dark');
    manager.classList.toggle('dark');
    forget.classList.toggle('dark');
    remember.classList.toggle('dark');
    container.classList.toggle('dark');
}
const setError = (element, message) => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error-message');
    errorDisplay.innerText = message;
    inputControl.classList.add('error-message');
    inputControl.classList.remove('success');
}

const setSuccess = element => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error-message');
    errorDisplay.innerText = '';
    inputControl.classList.add('success');
    inputControl.classList.remove('error-message');
}

const isValidpassword = password => {
    const regularexpression = /^(?=.*[a-z])(?=.*\d)(?=.*[A-Z])[^]{8,16}$/;
    return regularexpression.test(password);
}

function validateInputs() {
    const passwordValue = password.value.trim();//eliminate the spaces in the inputs
    const usernameValue = username.value.trim();
    if (usernameValue === '') {
        setError(username, 'Username is required');
    } else if (usernameValue.length > 20){
        setError(username, 'Username should be under 20 characters!');
    } else {
        setSuccess(username);
        success++;
    }
    if (passwordValue === '') {
        setError(password, 'Password is required');
    } else if (!isValidpassword(passwordValue)) {
        setError(password, 'Password must have numbers, upper and lower case letters, and between 8-16 characters');
    } else {
        setSuccess(password);
        success++;
    }
}

function LoginCheck() {
    success = 0;//check success is successful or not
    validateInputs();
    if (success != 2)//if not successful, return false
        return false;
    else {
        form.submit();//submit the form and let app render new page
        return true;
    }
}