import React, { ComponentType } from "react";
import { ListGroup, ListGroupItemProps } from "react-bootstrap";
import { Lock } from "react-bootstrap-icons";

import { Network } from "../../types";
import { NETWORK_AUTHMODES } from "../../utils";
import { RssiIcon } from "../RssiIcon";

type NetworkListItemProps = {
  network: Network | false;
} & ListGroupItemProps;

export const NetworkListItem: ComponentType<NetworkListItemProps> = ({
  network,
  ...props
}) => (
  <ListGroup.Item
    action
    className="d-flex justify-content-between align-items-center"
    {...props}
  >
    <span
      className={network === false ? "ms-4" : ""}
      title={network === false ? "" : network.bssid}
    >
      {network === false || <RssiIcon rssi={network.rssi} className="me-2" />}
      {network === false ? "other..." : network.ssid}
    </span>
    {network === false || network.authmode === 0 || (
      <span title={NETWORK_AUTHMODES[network.authmode]}>
        <Lock />
      </span>
    )}
  </ListGroup.Item>
);
