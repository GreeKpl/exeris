import {connect} from "react-redux";
import CharacterPage from "./CharacterPage";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const CharacterPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterPage);

export default CharacterPageContainer;
