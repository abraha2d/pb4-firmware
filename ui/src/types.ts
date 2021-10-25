export type RawNetwork = [
  string, // ssid
  string, // bssid
  1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11, // channel
  number, // rssi
  0 | 1 | 2 | 3 | 4, // authmode
  false // hidden
];

export type Network = {
  ssid: string;
  bssid: string;
  rssi: number;
  authmode: 0 | 1 | 2 | 3 | 4;
};
