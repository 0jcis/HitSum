document.addEventListener("DOMContentLoaded", function () {
  prefillFieldsFromUrl();
  initializeInputFields();
  updateTable();

  document.querySelectorAll(".table-sortable th").forEach(headerCell => {
    headerCell.addEventListener("click", () => {
      const tableElement = headerCell.closest('table');
      const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children,
        headerCell);
      const currentIsAscending = headerCell.classList.contains("th-sort-asc");
      sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
    });
  });

});

function copyUrlWithParams() {
  const url = new URL(window.location.href);

  // Define the mapping between input field IDs and URL parameter names
  const mapping = {
    'pay-per-war-attack': 'warAttackPay',
    'pay-per-assist': 'assistPay',
    'pay-per-chain-attack': 'chainAttackPay',
    'penalty-per-loss': 'penaltyForLosses'
  };

  // Update the URL parameters based on the current input values
  Object.keys(mapping).forEach(id => {
    const paramName = mapping[id];
    const value = document.getElementById(id).dataset.rawValue || 0;
    url.searchParams.set(paramName, value);  // Update existing parameter or add if not present
  });

  // Copy the URL to the clipboard
  navigator.clipboard.writeText(url.toString())
    .then(() => {
      const button = document.getElementById('copy-url-button');
      button.value = 'Copied!'; // Change button text

      // Change it back after 2 seconds
      setTimeout(() => {
        button.value = 'Copy with prefilled pay rates';
      }, 2000);
    })
    .catch(err => {
      console.error('Failed to copy URL: ', err);
    });
}

function prefillFieldsFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);

  const mapping = {
    'warAttackPay': 'pay-per-war-attack',
    'assistPay': 'pay-per-assist',
    'chainAttackPay': 'pay-per-chain-attack',
    'penaltyForLosses': 'penalty-per-loss'
  };

  Object.keys(mapping).forEach(param => {
    const value = urlParams.get(param);
    console.log(`URL Parameter for ${param}: ${value}`); // Log for debugging

    if (value !== null) { // Ensure the value is not null
      const inputId = mapping[param];
      const input = document.getElementById(inputId);
      input.value = formatMoney(value);
      input.dataset.rawValue = value;
    }
  });
}

function showFunction(elementId, link) {
  // Hide all elements with the class 'toggleElement'
  var elements = document.getElementsByClassName('hide');
  for (var i = 0; i < elements.length; i++) {
    elements[i].style.display = 'none';
  }

  // Show the selected element
  document.getElementById(elementId).style.display = 'block';

  // Remove 'active-link' class from all links
  var links = document.querySelectorAll('button');
  for (var j = 0; j < links.length; j++) {
    links[j].classList.remove('active-link');
  }

  // Add 'active-link' class to the clicked link
  link.classList.add('active-link');
}

function formatMoney(value) {
  if (typeof value !== 'string') {
    value = String(value); // Convert to string
  }
  value = value.replace(/\s/g, ''); // Remove spaces
  const numberValue = parseFloat(value);
  if (!isNaN(numberValue)) {
    return `$${numberValue.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}`;
  }
  return '$0'; // Default if not a number
}

function updateTable() {
  const warAttackPay = parseFloat(document.getElementById('pay-per-war-attack').dataset.rawValue) ||
    0;
  const assistPay = parseFloat(document.getElementById('pay-per-assist').dataset.rawValue) || 0;
  const chainAttackPay = parseFloat(
    document.getElementById('pay-per-chain-attack').dataset.rawValue) || 0;
  const penaltyForLosses = parseFloat(
    document.getElementById('penalty-per-loss').dataset.rawValue) || 0;

  let totalPayout = 0;

  document.querySelectorAll('tbody tr').forEach(row => {
    const warAttacks = parseFloat(row.cells[1].textContent.replace(/[$\s]/g, '')) || 0;
    const assists = parseFloat(row.cells[2].textContent.replace(/[$\s]/g, '')) || 0;
    const chainAttacks = parseFloat(row.cells[3].textContent.replace(/[$\s]/g, '')) || 0;
    const losses = parseFloat(row.cells[4].textContent.replace(/[$\s]/g, '')) || 0;

    const warAttackPayAmount = warAttacks * warAttackPay;
    const assistPayAmount = assists * assistPay;
    const chainAttackPayAmount = chainAttacks * chainAttackPay;
    const penaltyAmount = losses * penaltyForLosses;
    const finalPay = warAttackPayAmount + assistPayAmount + chainAttackPayAmount - penaltyAmount;


    console.log(row.cells[0].textContent);
    row.cells[5].textContent = formatMoney(warAttackPayAmount.toFixed(0));
    row.cells[6].textContent = formatMoney(assistPayAmount.toFixed(0));
    row.cells[7].textContent = formatMoney(chainAttackPayAmount.toFixed(0));
    row.cells[8].textContent = formatMoney(penaltyAmount.toFixed(0));
    row.cells[9].textContent = formatMoney(finalPay.toFixed(0));

    totalPayout += finalPay;
  });

  document.getElementById('total-payout').textContent = formatMoney(totalPayout.toFixed(0));
}

function initializeInputFields() {
  const inputFields = document.querySelectorAll('input.input-home');

  inputFields.forEach(input => {
    input.addEventListener('input', function () {
      const rawValue = this.value.replace(/[^0-9]/g, '');
      this.dataset.rawValue = rawValue;
      this.value = formatMoney(rawValue);
      updateTable();
    });

    input.addEventListener('blur', function () {
      const rawValue = this.value.replace(/[^0-9]/g, '');
      this.dataset.rawValue = rawValue;
      this.value = formatMoney(rawValue);
    });
  });
}

function sortTableByColumn(table, column, asc = true) {
  const dirModifier = asc ? 1 : -1;
  const tBody = table.tBodies[0];
  const rows = Array.from(tBody.querySelectorAll("tr"));

  const isNumeric = value => !isNaN(value.replace(/[\s$]/g, ''));
  const cleanNumber = value => {
    if (typeof value !== 'string') {
      value = String(value);
    }
    return parseFloat(value.replace(/[\s$]/g, '')) || 0;
  };

  const firstCellText = rows[0].querySelector(`td:nth-child(${column + 1})`).textContent.trim();
  const isNumericColumn = isNumeric(firstCellText);

  const sortedRows = rows.sort((a, b) => {
    const aColText = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
    const bColText = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();

    if (isNumericColumn) {
      return (cleanNumber(aColText) - cleanNumber(bColText)) * dirModifier;
    } else {
      return aColText.localeCompare(bColText) * dirModifier;
    }
  });

  tBody.append(...sortedRows);

  table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
  table.querySelector(`th:nth-child(${column + 1})`).classList.toggle("th-sort-asc", asc);
  table.querySelector(`th:nth-child(${column + 1})`).classList.toggle("th-sort-desc", !asc);
}
