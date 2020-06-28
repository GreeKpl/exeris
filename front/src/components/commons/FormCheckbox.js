import React from "react";
import {Col, Form, FormControl} from "react-bootstrap";
import "./style.scss";

class FormCheckbox extends React.Component {
  render() {
    const {
      feedbackIcon,
      input,
      label,
      type,
      meta: {error, warning, touched},
      ...props
    } = this.props;

    let message;
    let validationState = null;
    if (touched) {
      if (warning) {
        validationState = "warning";
      } else if (error) {
        validationState = "error";
      }
    }

    if (touched && (error || warning)) {
      message = <span className="help-block">{error || warning}</span>;
    }

    return <Form.Group validationState={validationState}>
      <Col componentClass={Form.Label} sm={3}>
        {label}
      </Col>
      <Col sm={9}>
        <Form.Check checked={typeof input.value === "boolean" ? input.value : false}
                    {...input}
                    className="FormCheckbox-Container"
                    type={type}
                    {...props}/>
      </Col>
      {feedbackIcon &&
      <FormControl.Feedback>{feedbackIcon}</FormControl.Feedback>}
      {message}
    </Form.Group>;
  }
}

export default FormCheckbox;
