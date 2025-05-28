const API_URL = 'http://127.0.0.1:5000/api';
let reportChart = null; // Store chart instance for updates

async function login() {
    const mobile = document.getElementById('mobile').value;
    const password = document.getElementById('password').value;
    try {
        const response = await axios.post(`${API_URL}/login`, { mobile, password });
        alert(response.data.message);
        document.getElementById('auth-section').classList.add('hidden');
        document.getElementById('app-section').classList.remove('hidden');
        loadCategories();
        loadExpenses();
        loadBudgets();
        loadReport();
        loadGpayTransactions();
    } catch (error) {
        alert(error.response.data.error);
    }
}

async function register() {
    const mobile = document.getElementById('reg-mobile').value;
    const password = document.getElementById('reg-password').value;
    try {
        const response = await axios.post(`${API_URL}/register`, { mobile, password });
        alert(response.data.message);
        showLogin();
    } catch (error) {
        alert(error.response.data.error);
    }
}

function showRegister() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
}

function showLogin() {
    document.getElementById('register-form').classList.add('hidden');
    document.getElementById('login-form').classList.remove('hidden');
}

function logout() {
    document.getElementById('app-section').classList.add('hidden');
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('mobile').value = '';
    document.getElementById('password').value = '';
    alert('Logged out successfully');
}

async function loadCategories() {
    const response = await axios.get(`${API_URL}/categories`);
    const categories = response.data;
    const expenseSelect = document.getElementById('expense-category');
    const budgetSelect = document.getElementById('budget-category');
    expenseSelect.innerHTML = '';
    budgetSelect.innerHTML = '';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        expenseSelect.appendChild(option.cloneNode(true));
        budgetSelect.appendChild(option);
    });
}

async function addExpense() {
    const date = document.getElementById('expense-date').value;
    const category = document.getElementById('expense-category').value;
    const amount = document.getElementById('expense-amount').value;
    const description = document.getElementById('expense-description').value;
    try {
        const response = await axios.post(`${API_URL}/expenses`, { date, category, amount, description });
        alert(response.data.message);
        loadExpenses();
        loadBudgets();
        updateReport(); // Auto-refresh chart
    } catch (error) {
        alert(error.response.data.error);
    }
}

async function loadExpenses() {
    const response = await axios.get(`${API_URL}/expenses`);
    const expenses = response.data;
    const table = document.getElementById('expense-table');
    table.innerHTML = '';
    expenses.forEach(expense => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-2">${expense.date}</td>
            <td class="p-2">${expense.category}</td>
            <td class="p-2">${expense.amount.toFixed(2)}</td>
            <td class="p-2">${expense.description}</td>
            <td class="p-2">
                <button onclick="editExpense('${expense.id}')" class="bg-yellow-500 text-white p-1 rounded">Edit</button>
                <button onclick="deleteExpense('${expense.id}')" class="bg-red-500 text-white p-1 rounded">Delete</button>
            </td>
        `;
        table.appendChild(row);
    });
}

async function editExpense(id) {
    const date = prompt('Enter new date (YYYY-MM-DD):');
    const category = prompt('Enter new category:');
    const amount = prompt('Enter new amount:');
    const description = prompt('Enter new description:');
    try {
        const response = await axios.put(`${API_URL}/expenses/${id}`, { date, category, amount, description });
        alert(response.data.message);
        loadExpenses();
        loadBudgets();
        updateReport(); // Auto-refresh chart
    } catch (error) {
        alert(error.response.data.error);
    }
}

async function deleteExpense(id) {
    if (confirm('Are you sure you want to delete this expense?')) {
        try {
            const response = await axios.delete(`${API_URL}/expenses/${id}`);
            alert(response.data.message);
            loadExpenses();
            loadBudgets();
            updateReport(); // Auto-refresh chart
        } catch (error) {
            alert(error.response.data.error);
        }
    }
}

async function setBudget() {
    const category = document.getElementById('budget-category').value;
    const amount = document.getElementById('budget-amount').value;
    try {
        const response = await axios.post(`${API_URL}/budgets`, { category, amount });
        alert(response.data.message);
        loadBudgets();
    } catch (error) {
        alert(error.response.data.error);
    }
}

async function loadBudgets() {
    const budgetResponse = await axios.get(`${API_URL}/budgets`);
    const expenseResponse = await axios.get(`${API_URL}/expenses`);
    const budgets = budgetResponse.data;
    const expenses = expenseResponse.data;
    const table = document.getElementById('budget-table');
    table.innerHTML = '';
    budgets.forEach(budget => {
        const spent = expenses
            .filter(expense => expense.category === budget.category)
            .reduce((sum, expense) => sum + expense.amount, 0);
        const remaining = budget.amount - spent;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-2">${budget.category}</td>
            <td class="p-2">${budget.amount.toFixed(2)}</td>
            <td class="p-2">${spent.toFixed(2)}</td>
            <td class="p-2 ${remaining < 0 ? 'text-red-500' : 'text-green-500'}">${remaining.toFixed(2)}</td>
        `;
        table.appendChild(row);
    });
}

async function loadReport() {
    const response = await axios.get(`${API_URL}/reports`);
    const report = response.data;
    const ctx = document.getElementById('report-chart').getContext('2d');
    reportChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: report.map(item => item.category),
            datasets: [{
                label: 'Spending by Category',
                data: report.map(item => item.total),
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

async function updateReport() {
    const response = await axios.get(`${API_URL}/reports`);
    const report = response.data;
    if (reportChart) {
        reportChart.data.labels = report.map(item => item.category);
        reportChart.data.datasets[0].data = report.map(item => item.total);
        reportChart.update();
    } else {
        loadReport(); // Fallback if chart not initialized
    }
}

async function syncGpayTransactions() {
    try {
        const response = await axios.post(`${API_URL}/gpay_transactions/sync`);
        alert(response.data.message);
        loadGpayTransactions();
    } catch (error) {
        alert(error.response.data.error);
    }
}

async function loadGpayTransactions() {
    try {
        const response = await axios.get(`${API_URL}/gpay_transactions`);
        const transactions = response.data;
        const table = document.getElementById('gpay-table');
        table.innerHTML = '';
        transactions.forEach(tx => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="p-2">${tx.date}</td>
                <td class="p-2">${tx.amount.toFixed(2)}</td>
                <td class="p-2">${tx.description}</td>
            `;
            table.appendChild(row);
        });
    } catch (error) {
        alert(error.response.data.error);
    }
}

// Initialize
loadCategories();