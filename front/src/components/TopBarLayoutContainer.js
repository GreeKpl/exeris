import {connect} from "react-redux";
import TopBarLayout from "./TopBarLayout";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    activePage: ownProps.activePage,
    characterActivePage: ownProps.characterActivePage,
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const TopBarLayoutContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopBarLayout);

export default TopBarLayoutContainer;
