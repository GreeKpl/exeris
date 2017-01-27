import React from "react";
import {FormGroup, ControlLabel, Col, ListGroup, ListGroupItem} from "react-bootstrap";

class HorizontalFormInfo extends React.Component {
  render() {
    const {label, lines} = this.props;

    return <FormGroup>
      <Col componentClass={ControlLabel} sm={3}>
        {label}
      </Col>
      <Col sm={9}>
        <ListGroup>
          {lines.map(line => <ListGroupItem key={line}>{line}</ListGroupItem>)}
        </ListGroup>
      </Col>
    </FormGroup>;
  }
}
export default HorizontalFormInfo;
