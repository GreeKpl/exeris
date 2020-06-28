import {connect} from "react-redux";
import {fromPlayerState, getAchievementsList, requestAchievementsList} from "../../modules/player";
import React from "react";
import {Card, ListGroup, ListGroupItem} from "react-bootstrap";

const AchievementEntry = ({title, children}) => (
  <ListGroupItem header={title}>
    {children}
  </ListGroupItem>
);

class AchievementsList extends React.Component {
  componentDidMount() {
    this.props.onMount();
  }

  render() {
    return (
      <Card>
        <Card.Header>Achievements</Card.Header>
        <Card.Body>
          <ListGroup>
            {this.props.achievements.map(achievement =>
              <AchievementEntry key={achievement.get("title")}
                                title={achievement.get("title")}>
                {achievement.get("content")}
              </AchievementEntry>
            )}
          </ListGroup>
        </Card.Body>
      </Card>
    );
  }
}

export {AchievementsList};

const mapStateToProps = (state) => {
  return {achievements: getAchievementsList(fromPlayerState(state))};
};

const mapDispatchToProps = (dispatch) => {
  return {
    onMount: () => dispatch(requestAchievementsList()),
  }
};

const AchievementsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(AchievementsList);

export default AchievementsListContainer;
