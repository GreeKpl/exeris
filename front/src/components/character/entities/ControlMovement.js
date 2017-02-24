import React from "react";
import {Panel, Form, FormGroup, FormControl, ControlLabel, Button} from "react-bootstrap";

class ControlMovement extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Panel header="Control movement">
        <Form autoComplete="off" inline>
          <FormGroup controlId="travelDirection">
            <ControlLabel>Direction</ControlLabel>
            {' '}
            <FormControl type="number" placeholder="Set degrees..."/>
          </FormGroup>
          {' '}
          <Button type="submit">
            Set travel direction
          </Button>
        </Form>
      </Panel>);
  }
}

export default ControlMovement;
