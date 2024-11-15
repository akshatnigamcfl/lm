function confirmationPopUp(title, message, data){
    const popup = document.createElement('div');
    popup.classList.value = 'w-screen h-screen absolute top-0 left-0 flex justify-center items-center bg-[rgba(0,0,0,0.7)]'
    popup.innerHTML = `
    <div class="card w-96 bg-white text-neutral-content">
        <div class="card-body items-center text-center">
        <h2 class="card-title text-slate-900 capitalize">${title}</h2>
        <p class="text-slate-900 capitalize">${message}</p>
        <div class="card-actions justify-end">
          <button data-user-id="${data}" class="confirm_btn btn btn-primary">Accept</button>
          <button class=" close_btn btn btn-ghost text-slate-900">Deny</button>
        </div>
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

}



