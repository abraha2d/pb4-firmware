import { Network, RawNetwork } from "./types";

export enum NETWORK_AUTHMODES {
  Open,
  WEP,
  WPA_PSK,
  WPA2_PSK,
  WPA_WPA2_PSK,
}

export const parseNetworks = (rawNetworks: RawNetwork[]) =>
  rawNetworks
    .map(
      (n): Network => ({
        ssid: n[0],
        bssid: n[1],
        rssi: n[3],
        authmode: n[4],
      })
    )
    .sort((a, b) => b.rssi - a.rssi || a.ssid.localeCompare(b.ssid))
    .filter(
      (network, i, ns) =>
        ns.findIndex(
          (n) => n.ssid === network.ssid && n.authmode === network.authmode
        ) === i
    );
