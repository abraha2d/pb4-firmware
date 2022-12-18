import React, { ComponentType } from "react";
import { IconProps, Wifi, Wifi1, Wifi2 } from "react-bootstrap-icons";

type RssiIconProps = {
  rssi: number;
} & IconProps;

export const RssiIcon: ComponentType<RssiIconProps> = ({ rssi, ...props }) => {
  if (rssi < -80) {
    return <Wifi1 {...props} />;
  } else if (rssi < -67) {
    return <Wifi2 {...props} />;
  } else {
    return <Wifi {...props} />;
  }
};
