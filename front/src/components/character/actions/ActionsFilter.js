import React from "react";
import {FormControl, FormGroup} from "react-bootstrap";

class ActionsFilter extends React.Component {

  constructor(props) {
    super(props);

    this.onSubmit = this.onSubmit.bind(this);
  }

  render() {
    return (
      <form autoComplete="off" onSubmit={this.onSubmit}>
        <FormGroup
          controlId="actionsFilter">
          <FormControl
            type="text"
            value={this.props.filterText}
            placeholder="Enter filter text..."
            onChange={this.props.onChange}
          />
        </FormGroup>
      </form>);
  }

  onSubmit(event) {
    event.preventDefault();
  }
}

export default ActionsFilter;
