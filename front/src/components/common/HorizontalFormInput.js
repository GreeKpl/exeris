import React from "react";
import {FormGroup, FormControl, ControlLabel, Col} from "react-bootstrap";

class HorizontalFormInput extends React.Component {
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

    return <FormGroup validationState={validationState}>
      <Col componentClass={ControlLabel} sm={3}>
        {label}
      </Col>
      <Col sm={9}>
        <FormControl {...input}
                     type={type}
                     {...props}/>
      </Col>
      {feedbackIcon &&
      <FormControl.Feedback>{ feedbackIcon }</FormControl.Feedback>}
      {message}
    </FormGroup>;
  }
}
export default HorizontalFormInput;
