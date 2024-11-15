// function userEditPopUp(){
//     const popup = document.createElement('div');
//     popup.classList.value = 'w-screen h-screen absolute top-0 left-0 flex justify-center items-center bg-[rgba(0,0,0,0.7)] '
//     popup.innerHTML = `

//     <div class="card w-[600px] h-[500px] bg-white text-neutral-content overflow-hidden">
//     <div class="h-[35px] flex justify-center items-center text-white bg-slate-900">View/Edit User</div>
//     <div class="h-[40px] flex justify-end items-center text-white px-4">
//       <label class="flex justify-center text-slate-900"><span>Edit</span><input type="checkbox" class="edit_toggle toggle ml-3" /><label>
//     </div>
//     <div class="h-[calc(100%-75px)] w-full flex justify-between flex-wrap p-3 overflow-y-scroll">

//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="employee id" name="employee_id">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="name" name="name">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl " placeholder="email id" name="email_id">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl " placeholder="contact number" name="contact_number">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="department" name="department">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="designation" name="designation">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="employee status" name="employee_status">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="director" name="director">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="user manager" name="user_manager">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="lead manager" name="lead_manager">
//       <input disabled type="text" class="inps border flex w-[40%] h-10 px-2 rounded-xl  capitalize" placeholder="team leader" name="team_leader">
      
//       <select class="inps border w-[40%] h-10 px-2 rounded-xl" placeholder="segment" name="segment">
//         <option>e commerce</option>
//       </select>
      
//       <select><input type="text" class="inps border w-[40%] h-10 px-2 rounded-xl " placeholder="service" name="service"></select>
//       <select><input type="text" class="inps border w-[40%] h-10 px-2 rounded-xl " placeholder="marketplace" name="marketplace"></select>
//       <select><input type="text" class="inps border w-[40%] h-10 px-2 rounded-xl " placeholder="program" name="program"></select>
//       <select><input type="text" class="inps border w-[40%] h-10 px-2 rounded-xl " placeholder="sub program" name="sub_program"></select>
//     </div>
//     </div>
//     `
//     document.body.append(popup)


//     const close_btn = popup.querySelectorAll('.close_btn');
//     close_btn.forEach(e=>{
//         e.addEventListener('click',()=>{
//             popup.remove()
//         })
//     })

//     const edit_toggle = popup.querySelector('.edit_toggle');
//     edit_toggle.addEventListener('click',()=>{
//       const inps = document.querySelectorAll('.inps');

//       inps.forEach(e=>{
//         if (edit_toggle.checked){
//           e.disabled = true
//         } else {
//           e.disabled = false
//         }
//       })
//     })

// }



