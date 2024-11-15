const tool_tip = document.querySelectorAll('.tool_tip');
tool_tip.forEach(e=>{

    e.addEventListener('mouseenter',()=>{
        e.classList.add('tooltip')
    })
    e.addEventListener('mouseleave',()=>{
        e.classList.remove('tooltip')
    })

})
