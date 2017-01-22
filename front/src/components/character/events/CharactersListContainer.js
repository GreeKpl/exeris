import {connect} from "react-redux";
import CharactersList from "./CharactersList";
import {
  fromCharactersAroundState,
  getCharactersAround,
  requestCharactersAround
} from "../../../modules/charactersAround";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    charactersAround: getCharactersAround(fromCharactersAroundState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestCharactersAround(ownProps.characterId)),
  }
};

const CharactersListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharactersList);

export default CharactersListContainer;
