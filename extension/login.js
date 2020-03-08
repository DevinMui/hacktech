const submit = document.querySelector('#submit-btn')
let isSubmitting = false
submit.addEventListener(submit)
function submit() {
    if(isSubmitting) return
    isSubmitting = true
    const email = document.querySelector('#email').value
    const pw = document.querySelector('#password').value
    // TODO: do a post 
    submit.value = 'Signing in...'
    setTimeout(submitSuccess, 3000)
}

function submitSuccess(auth) {
    chrome.storage.sync.set({auth: auth})
    window.location=document.referrer;
}

function submitFail() {
    submit.value = 'Sign in'
    isSubmitting = false
    Snackbar.show({ text: 'Incorrect credentials', showAction: false, pos:'bottom-center' });
}