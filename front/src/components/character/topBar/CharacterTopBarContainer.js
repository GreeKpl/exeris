import {connect} from "react-redux";
import CharacterTopBar from "./CharacterTopBar";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    activePage: ownProps.activePage,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const CharacterTopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterTopBar);

export default CharacterTopBarContainer;
