import React, { useEffect, useState } from "react";
import {
  Button,
  Card,
  Col,
  Container,
  FloatingLabel,
  Form,
  ListGroup,
  Row,
  Spinner,
} from "react-bootstrap";

import NetworkListItem from "./components/NetworkListItem";
import { RefreshButton } from "./components/RefreshButton";
import { Network } from "./types";
import { parseNetworks } from "./utils";

const App = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [macAddress, setMacAddress] = useState("...");
  const [networks, setNetworks] = useState<Network[]>([]);
  const [selectedNetwork, setSelectedNetwork] = useState<Network | false>();
  const [ssid, setSsid] = useState("");
  const [password, setPassword] = useState("");
  const [isConnecting, setIsConnecting] = useState(false);

  const fetchMacAddress = () => {
    fetch("/id")
      .then((r) => r.text())
      .then(setMacAddress);
  };

  const fetchNetworks = () => {
    setIsLoading(true);
    fetch("/scan")
      .then((r) => r.json())
      .then(parseNetworks)
      .then(setNetworks)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchMacAddress();
    fetchNetworks();
  }, []);

  const isNetworkSelected = (n: Network | false) =>
    n === false
      ? selectedNetwork === n
      : selectedNetwork && n.bssid === selectedNetwork.bssid;

  const handleSelectNetwork = (n: Network | false) => () => {
    setSelectedNetwork(isNetworkSelected(n) ? undefined : n);
  };

  return (
    <Container className="py-3">
      <Row className="justify-content-center">
        <Col xxl={5} xl={6} lg={7} md={9} sm={12}>
          <Card>
            <Card.Header>
              <h1 className="display-6 text-center">pb4 setup</h1>
            </Card.Header>

            <Card.Body>
              <div className="mb-3 d-flex justify-content-between align-items-center">
                <div className="d-flex flex-column">
                  <span className="lead">wi-fi networks</span>
                  <small className="text-muted">select a network</small>
                </div>

                <RefreshButton
                  disabled={isConnecting}
                  loading={isLoading}
                  onClick={fetchNetworks}
                  variant=""
                />
              </div>

              <ListGroup>
                {networks.map((n) => (
                  <NetworkListItem
                    key={n.bssid}
                    active={isNetworkSelected(n)}
                    disabled={isConnecting}
                    network={n}
                    onClick={handleSelectNetwork(n)}
                  />
                ))}
                <NetworkListItem
                  active={isNetworkSelected(false)}
                  disabled={isConnecting}
                  network={false}
                  onClick={handleSelectNetwork(false)}
                />
              </ListGroup>

              <Form
                action="/connect"
                method="GET"
                onSubmit={() => setIsConnecting(true)}
              >
                {selectedNetwork === false ? (
                  <FloatingLabel className="mt-3" label="ssid">
                    <Form.Control
                      maxLength={32}
                      name="ssid"
                      onChange={(e) => setSsid(e.target.value)}
                      readOnly={isConnecting}
                      required
                      value={ssid}
                    />
                  </FloatingLabel>
                ) : (
                  selectedNetwork && (
                    <input
                      name="ssid"
                      type="hidden"
                      value={selectedNetwork.ssid}
                    />
                  )
                )}

                {(selectedNetwork === false ||
                  (selectedNetwork && selectedNetwork.authmode !== 0)) && (
                  <FloatingLabel className="mt-3" label="password">
                    <Form.Control
                      autoComplete="new-password"
                      minLength={5}
                      maxLength={63}
                      name="password"
                      onChange={(e) => setPassword(e.target.value)}
                      readOnly={isConnecting}
                      required={selectedNetwork !== false}
                      type="password"
                      value={password}
                    />
                  </FloatingLabel>
                )}

                <div className="mt-3 d-flex justify-content-between align-items-center">
                  <small className="text-muted">
                    device mac address: {macAddress}
                  </small>

                  <Button
                    disabled={selectedNetwork === undefined || isConnecting}
                    type="submit"
                    variant={
                      selectedNetwork === undefined
                        ? "outline-secondary"
                        : isConnecting
                        ? "outline-primary"
                        : "primary"
                    }
                  >
                    {isConnecting && (
                      <Spinner animation="border" className="me-1" size="sm" />
                    )}

                    {isConnecting ? "Connecting..." : "Connect"}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default App;
