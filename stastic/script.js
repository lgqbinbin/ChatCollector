// JavaScript 文件：script.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('userForm');
    const tableBody = document.querySelector('#userTable tbody');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const userId = document.getElementById('userId').value;
        const name = document.getElementById('name').value;
        const grade = document.getElementById('grade').value;
        const major = document.getElementById('major').value;
        const expertise = document.getElementById('expertise').value;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${userId}</td>
            <td>${name}</td>
            <td>${grade}</td>
            <td>${major}</td>
            <td>${expertise}</td>
        `;
        tableBody.appendChild(row);

        // 清空表单
        form.reset();
    });
});
