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

document.addEventListener("DOMContentLoaded", function () {
  const moneyElements = document.querySelectorAll('.money');

  moneyElements.forEach(function (element, index) {
    console.log(`Element ${index}:`, element.textContent);
    formatMoney(element);
  });
});

function formatMoney(element) {
  const value = parseFloat(element.textContent);
  if (!isNaN(value)) {
    const formattedValue = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    console.log("Formatted value:", formattedValue); // Debugging line
    element.textContent = formattedValue;
  }
}
