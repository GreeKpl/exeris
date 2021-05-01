import {connect} from "react-redux";
import {fromRecipesState, getFilterText, updateFilterText} from "../../../modules/recipes";
import React from "react";
import {Form} from "react-bootstrap";

export class ActionsFilter extends React.Component {

  constructor(props) {
    super(props);

    this.onSubmit = this.onSubmit.bind(this);
  }

  render() {
    return (
      <form autoComplete="off" onSubmit={this.onSubmit}>
        <Form.Group
          controlId="actionsFilter">
          <Form.Control
            type="text"
            value={this.props.filterText}
            placeholder="Enter filter text..."
            onChange={this.props.onChange}
          />
        </Form.Group>
      </form>);
  }

  onSubmit(event) {
    event.preventDefault();
  }
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    filterText: getFilterText(fromRecipesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onChange: event => dispatch(updateFilterText(ownProps.characterId, event.target.value)),
  }
};

const ActionsFilterContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsFilter);

export default ActionsFilterContainer;
