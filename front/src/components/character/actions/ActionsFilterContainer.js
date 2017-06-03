import {connect} from "react-redux";
import {
  getFilterText,
  fromRecipesState,
  updateFilterText
} from "../../../modules/recipes";
import React from "react";
import {FormControl, FormGroup} from "react-bootstrap";

export class ActionsFilter extends React.Component {

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
