import React from "react";
import {Form, FormGroup, Col, FormControl, ControlLabel, Button} from "react-bootstrap";

class ActionDetails extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Form horizontal>
        <FormGroup controlId="actionName">
          <Col componentClass={ControlLabel} sm={3}>
            Name
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            Forging a sword
          </Col>
        </FormGroup>

        <FormGroup controlId="activitySubject">
          <Col componentClass={ControlLabel} sm={3}>
            Subject of activity
          </Col>
          <Col sm={9}>
            <FormControl componentClass="select" placeholder="Select subject...">
              <option value={1}>Bronze anvil</option>
              <option value={45}>Iron anvil</option>
            </FormControl>
          </Col>
        </FormGroup>
        <FormGroup controlId="requiredInput">
          <Col componentClass={ControlLabel} sm={3}>
            Required input
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            1 bar of metal
          </Col>
        </FormGroup>
        <FormGroup controlId="requiredTools">
          <Col componentClass={ControlLabel} sm={3}>
            Required tools
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            a smith hammer
          </Col>
        </FormGroup>
        <FormGroup controlId="requiredMachines">
          <Col componentClass={ControlLabel} sm={3}>
            Required machines
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            an anvil
          </Col>
        </FormGroup>
        <FormGroup controlId="requiredDays">
          <Col componentClass={ControlLabel} sm={3}>
            Required days
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            8 = 4 x 2
          </Col>
        </FormGroup>
        <FormGroup controlId="requiredSkill">
          <Col componentClass={ControlLabel} sm={3}>
            Required skills
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            50 Smithing
          </Col>
        </FormGroup>

        <FormGroup controlId="resultAmount">
          <Col componentClass={ControlLabel} sm={3}>
            Amount
          </Col>
          <Col sm={9}>
            <FormControl type="text" placeholder="amount" value="2" readOnly/>
          </Col>
        </FormGroup>

        <FormGroup>
          <Col smOffset={3} sm={9}>
            <Button type="submit">
              Start an activity
            </Button>
          </Col>
        </FormGroup>
      </Form>);
  }
}

export default ActionDetails;
