let selectedNetwork = null;

const pb4Init = () => {
  const refreshButton = document.getElementById('refresh-button');
  const networkList = document.getElementById('network-list');
  const connectForm = document.getElementById('connect-form');
  const ssidWrapper = document.getElementById('ssid-wrapper');
  const ssidField = document.getElementById('ssid');
  const passwordWrapper = document.getElementById('pass-wrapper');
  const passwordField = document.getElementById('password');
  const connectStage0 = document.getElementById('connect-stage0');
  const connectStage1 = document.getElementById('connect-stage1');
  const connectStage2 = document.getElementById('connect-stage2');

  refreshButton.onclick = () => {
    refreshButton.setAttribute('disabled', 'disabled');
    refreshButton.firstElementChild.classList.add('d-none');
    refreshButton.lastElementChild.classList.remove('d-none');
    location.reload();
  };

  for (let n of networkList.children) {
    n.onclick = () => {
      if (n === selectedNetwork) {
        selectedNetwork = null;
        n.classList.remove('active');
        ssidWrapper.classList.add('d-none');
        passwordWrapper.classList.add('d-none');
        connectStage0.classList.remove('d-none');
        connectStage1.classList.add('d-none');
      } else {
        if (selectedNetwork === null) {
          connectStage0.classList.add('d-none');
          connectStage1.classList.remove('d-none');
        } else {
          selectedNetwork.classList.remove('active');
        }
        n.classList.add('active');
        selectedNetwork = n;

        if (n.childElementCount === 2) {
          ssidWrapper.classList.add('d-none');
          passwordWrapper.classList.remove('d-none');
          ssidField.value = n.firstElementChild.textContent.trim();
          passwordField.setAttribute('required', 'required');
        } else if (n.id === 'other') {
          ssidWrapper.classList.remove('d-none');
          passwordWrapper.classList.remove('d-none');
          ssidField.value = '';
          passwordField.removeAttribute('required');
        } else {
          ssidWrapper.classList.add('d-none');
          passwordWrapper.classList.add('d-none');
          ssidField.value = n.firstElementChild.textContent.trim();
          passwordField.value = '';
          passwordField.removeAttribute('required');
        }
      }
    };
  }

  connectForm.onsubmit = () => {
    refreshButton.setAttribute('disabled', 'disabled');
    for (let n of networkList.children) {
      n.setAttribute('disabled', 'disabled');
    }
    ssidField.setAttribute('readonly', 'readonly');
    passwordField.setAttribute('readonly', 'readonly');
    connectStage1.classList.add('d-none');
    connectStage2.classList.remove('d-none');
  };
};

document.addEventListener('DOMContentLoaded', pb4Init, false);
