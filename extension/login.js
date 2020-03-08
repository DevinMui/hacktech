const submit = document.querySelector('#submit-btn')
let isSubmitting = false
submit.addEventListener('click', submitFn)
function submitFn() {
    if(isSubmitting) return
    isSubmitting = true
    const email = document.querySelector('#email').value
    const pw = document.querySelector('#password').value
    // TODO: do a post 
    // submit.value = 'Signing in...'
    document.querySelector('.login-box').innerHTML = `
    <img style="transform: translate(-25%, 10%)" src="loader.gif"></img>
    <h1>Please wait while we load your credentials...</h1>`
    setTimeout(() => submitSuccess(), 5000)
}

function submitSuccess(auth) {
    chrome.storage.sync.set({auth: auth})
    window.close()
}

function submitFail() {
    submit.value = 'Sign in'
    isSubmitting = false
    Snackbar.show({ text: 'Incorrect credentials', showAction: false, pos:'bottom-center' });
}