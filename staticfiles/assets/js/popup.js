function addPopUp(h, w, title,){
    const popup  = document.createElement('div')
    popup.classList.value = 'w-screen h-screen fixed top-0 left-0 flex justify-center items-center bg-[rgba(0,0,0,0.7)]'
    
    popup.innerHTML = `
    
    <div class="card w-${w} h-${h} bg-white text-neutral-content overflow-hidden">
        <div class="h-[35px] relative flex justify-center items-center text-white bg-slate-900">${title}</div>
        <img class="close_btn absolute h-6 w-6 top-[5px] right-[5px]" src="/static/assets/images/close_button.png">
        <div class="main_body h-[calc(100%-35px)] w-full flex justify-between flex-wrap p-3 bg-gray-50 text-slate-900 text-xs">
        </div>
    </div>
    `
    document.body.append(popup)

    const close_btn = popup.querySelectorAll('.close_btn');
    close_btn.forEach(e=>{
        e.addEventListener('click',()=>{
            popup.remove()
        })
    })

    return popup.querySelector('.main_body')

//     popup.innerHTML = `
}
