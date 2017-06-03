import {connect} from "react-redux";
import {
  getFilteredRecipes,
  fromRecipesState,
  requestRecipesList,
  selectRecipe
} from "../../../modules/recipes";

import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";

class ActionsListItem extends React.Component {
  constructor(props) {
    super(props);

    this.handleClick = this.handleClick.bind(this);
  }

  render() {
    return <ListGroupItem onClick={this.handleClick}
                          disabled={!this.props.action.get("enabled")}>
      {this.props.action.get("name")}
    </ListGroupItem>;
  }

  handleClick() {
    this.props.onSelectAction(this.props.action.get("id"));
  }
}

export class ActionsList extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  render() {
    return (
      <ListGroup>
        {this.props.actionsList.map(action =>
          <ActionsListItem onSelectAction={this.props.onSelectAction}
                           action={action}
                           key={action.get("id")}/>)}

      </ListGroup>);
  }
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    actionsList: getFilteredRecipes(fromRecipesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSelectAction: actionId =>
      dispatch(selectRecipe(ownProps.characterId, actionId)),
    requestState: () => dispatch(requestRecipesList(ownProps.characterId))
  }
};

const ActionsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsList);

export default ActionsListContainer;
