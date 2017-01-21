import React from "react";
import {FormControl, FormGroup} from "react-bootstrap";

class ActionsFilter extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <form>
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
}

export default ActionsFilter;
