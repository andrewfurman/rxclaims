function createMemberGPT() {
  const button = document.getElementById('createGPTButton');
  const prompt = document.getElementById('gptPrompt').value;

  // Disable button and show loading state
  button.disabled = true;
  button.innerHTML = `
    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    Processing...
  `;
  // Make API call
  fetch('/members/create-gpt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt: prompt })
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
    }
    // Refresh the page
    window.location.reload();
  })
  .catch(error => {
    alert('Error creating member');
    button.disabled = false;
    button.innerHTML = 'Create Member GPT';
  });
}

function exportMembers() {
  const button = document.getElementById('exportButton');
  
  // Disable button and show loading state
  button.disabled = true;
  button.innerHTML = `
    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    Exporting...
  `;

  // Make API call
  fetch('/members/export', {
    method: 'GET',
  })
  .then(response => response.blob())
  .then(blob => {
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `members_export.xlsx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    
    // Reset button
    button.disabled = false;
    button.innerHTML = '📥 Export Members';
  })
  .catch(error => {
    alert('Error exporting members');
    button.disabled = false;
    button.innerHTML = '📥 Export Members';
  });
}