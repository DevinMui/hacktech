
const h = `<h1 style="margin-bottom: 2rem;">Login</h1>
<div class="textbox">
    <input id="email" type="text" style="width: 100%;" placeholder="Email" name="" value="ebayuser@ebay.com">
</div>

<div class="textbox">
    <input id="password" type="password" style="width: 100%;" placeholder="Password" name="" value="password123">
</div>

<input id="submit-btn" class="btn" type="button" name="" value="Sign in">`
document.querySelector('.login-box').innerHTML = h
let submit = document.querySelector('#submit-btn')
submit.addEventListener('click', submitFn)

let isSubmitting = false

async function submitFn() {
    if (isSubmitting) return
    isSubmitting = true
    const email = document.querySelector('#email').value
    const pw = document.querySelector('#password').value
    document.querySelector('.login-box').innerHTML = `
    <img style="transform: translate(-25%, 10%)" src="loader.gif"></img>
    <h1>Please wait while we process your credentials...</h1>`
    try {
        let r = await fetch('https://hacktech-ebay.appspot.com/login', {
            method: 'POST',
            mode: 'cors',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email })
        })
        r = await r.json()
        if (r.error) {
            return submitFail()
        }
        else {
            return submitSuccess(r._id)
        }
    } catch (e) {
        console.log(e)
        submitFail()
    }
}

function submitSuccess(auth) {
    chrome.storage.sync.set({ auth: auth }, console.log)
    document.querySelector('.login-box').innerHTML = `<h1>You're now logged in. It's safe to close this window.</h1>`
}

function submitFail() {
    submit.value = 'Sign in'
    isSubmitting = false
    document.querySelector('.login-box').innerHTML = h
    submit = document.querySelector('#submit-btn')
    submit.addEventListener('click', submitFn)
    Snackbar.show({ text: 'Incorrect credentials', showAction: false, pos: 'bottom-center' });
}
