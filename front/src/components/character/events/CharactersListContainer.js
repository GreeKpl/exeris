import {connect} from "react-redux";
import CharactersList from "./CharactersList";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.params};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const CharactersListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharactersList);

export default CharactersListContainer;
