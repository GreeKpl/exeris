import React from "react";
import {Col, Form, ListGroup, ListGroupItem} from "react-bootstrap";

class HorizontalFormInfo extends React.Component {
  render() {
    const {label, lines} = this.props;

    return <Form.Group>
      <Col componentClass={Form} sm={3}>
        {label}
      </Col>
      <Col sm={9}>
        <ListGroup>
          {lines.map(line => <ListGroupItem key={line}>{line}</ListGroupItem>)}
        </ListGroup>
      </Col>
    </Form.Group>;
  }
}

export default HorizontalFormInfo;
