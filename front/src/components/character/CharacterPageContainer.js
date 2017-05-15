import {connect} from "react-redux";
import CharacterPage from "./CharacterPage";
import {fromPlayerState, getOwnCharactersList, requestOwnCharactersList} from "../../modules/player";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
    characterIdsList: getOwnCharactersList(fromPlayerState(state)),
    characterPageUrl: /character\/\d+\/([^/]+)/.exec(ownProps.location.pathname)[1],
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    requestState: () => {
      dispatch(requestOwnCharactersList());
    },
  }
};

const CharacterPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterPage);

export default CharacterPageContainer;
