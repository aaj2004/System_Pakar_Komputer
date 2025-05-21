document.addEventListener('DOMContentLoaded', () => {
  const inputs = document.querySelectorAll('input[type="number"]');
  inputs.forEach(input => {
    input.addEventListener('input', () => {
      if (input.value > 1) input.value = 1;
      if (input.value < 0) input.value = 0;
    });
  });
});
