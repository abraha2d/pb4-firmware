let selectedNetwork = null;


const handleClickNetwork = (n) => () => {
  const ssidWrapper = document.getElementById('ssid-wrapper');
  const ssidField = document.getElementById('ssid');
  const passwordWrapper = document.getElementById('pass-wrapper');
  const passwordField = document.getElementById('password');
  const connectStage0 = document.getElementById('connect-stage0');
  const connectStage1 = document.getElementById('connect-stage1');

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


const handleSubmit = () => {
  const refreshButton = document.getElementById('refresh-button');
  refreshButton.setAttribute('disabled', 'disabled');

  const networkList = document.getElementById('network-list');
  for (let n of networkList.children) {
    n.setAttribute('disabled', 'disabled');
  }

  const ssidField = document.getElementById('ssid');
  ssidField.setAttribute('readonly', 'readonly');

  const passwordField = document.getElementById('password');
  passwordField.setAttribute('readonly', 'readonly');

  const connectStage1 = document.getElementById('connect-stage1');
  connectStage1.classList.add('d-none');

  const connectStage2 = document.getElementById('connect-stage2');
  connectStage2.classList.remove('d-none');
};


const updateNetworkList = (networks) => {
  const refreshButton = document.getElementById('refresh-button');
  const networkList = document.getElementById('network-list');
  const otherNetwork = document.getElementById("other");

  if (selectedNetwork) {
    handleClickNetwork(selectedNetwork)();
  }

  while (networkList.firstChild) {
    networkList.removeChild(networkList.firstChild);
  }

  networkList.append(...Object.values(networks).map(network => {
    const button = document.createElement('button');
    button.setAttribute('class',
      'list-group-item list-group-item-action d-flex justify-content-between');
    button.onclick = handleClickNetwork(button);

    const span = document.createElement('span');
    button.append(span);

    const i1 = document.createElement('i');
    i1.setAttribute('class', 'bi-wifi me-2');
    span.append(i1);

    span.append(network.ssid);

    if (network.authmode !== 0) {
      const i2 = document.createElement('i');
      i2.setAttribute('class', 'bi-lock');
      button.append(i2);
    }

    return button;
  }), otherNetwork);

  refreshButton.lastElementChild.classList.add('d-none');
  refreshButton.firstElementChild.classList.remove('d-none');
  refreshButton.removeAttribute('disabled');
};


const refreshNetworkList = () => {
  const refreshButton = document.getElementById('refresh-button');
  refreshButton.setAttribute('disabled', 'disabled');
  refreshButton.firstElementChild.classList.add('d-none');
  refreshButton.lastElementChild.classList.remove('d-none');

  fetch('/scan').then(r => r.json()).then(r => {
    const networks = {};
    r.forEach(n => {
      if ([n[0], n[4]] in r) {
        const network = networks[[n[0], n[4]]];
        network.rssi = Math.max(network.rssi, n[3]);
      } else {
        networks[[n[0], n[4]]] = {
          ssid: n[0],
          rssi: n[3],
          authmode: n[4],
        };
      }
    });
    return networks;
  }).then(r => updateNetworkList(r));
};


const pb4Init = () => {
  const refreshButton = document.getElementById('refresh-button');
  refreshButton.onclick = refreshNetworkList;
  refreshNetworkList();

  const otherNetwork = document.getElementById("other");
  otherNetwork.onclick = handleClickNetwork(otherNetwork);

  const connectForm = document.getElementById('connect-form');
  connectForm.onsubmit = handleSubmit;
};


document.addEventListener('DOMContentLoaded', pb4Init, false);
