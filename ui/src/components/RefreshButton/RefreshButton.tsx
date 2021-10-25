import React, { ComponentType } from "react";
import { Button, ButtonProps, Spinner } from "react-bootstrap";
import { ArrowClockwise } from "react-bootstrap-icons";

type RefreshButtonProps = {
  loading: boolean;
} & ButtonProps;

export const RefreshButton: ComponentType<RefreshButtonProps> = ({
  loading,
  ...props
}) => (
  <Button {...props}>
    {loading ? <Spinner animation="border" size="sm" /> : <ArrowClockwise />}
  </Button>
);
