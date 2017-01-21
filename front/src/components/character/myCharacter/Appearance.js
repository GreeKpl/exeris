import React from "react";
import {FormGroup, ControlLabel, FormControl, Form, Col} from "react-bootstrap";

class Appearance extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Form horizontal>

        <FormGroup controlId="shortDescriptionTextarea">
          <Col componentClass={ControlLabel} sm={3}>
            Short description
          </Col>
          <Col sm={9}>
            <FormControl componentClass="textarea"
                         placeholder="Enter short description shown directly on characters list..." rows={1}/>
          </Col>
        </FormGroup>
        <FormGroup controlId="longDescriptionTextarea">
          <Col componentClass={ControlLabel} sm={3}>
            Long description
          </Col>
          <Col sm={9}>
            <FormControl componentClass="textarea" placeholder="Enter long description..."/>
          </Col>
        </FormGroup>
      </Form>);
  }
}

export default Appearance;
