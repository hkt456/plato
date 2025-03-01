import { Session } from "../models/Session";
import { SessionService } from "./SessionService";
import { SessionDocument } from "../models/SessionDocument";
import { SessionRepository } from "../repo/SessionRepository";

export class SessionServiceImpl implements SessionService {

    private sessionRepository: SessionRepository;

    constructor(sessionRepository: SessionRepository) {
        this.sessionRepository = sessionRepository;
    }

    public getSessionBySessionId(sessionId: string): Promise<Session | null> {
        const session = this.sessionRepository.getSessionBySessionId(sessionId);
        return session.then((sessionDocument: SessionDocument | null) => {
            if (sessionDocument === null) {
                return null;
            }
            return this.fromDocument(sessionDocument);
        });
    }

    public getSessionByUserId(userId: string): Promise<Session[]> {
        const sessions = this.sessionRepository.getSessionByUserId(userId);
        return sessions.then((sessionDocuments: SessionDocument[] | null) => {
            if (sessionDocuments === null) {
                return [];
            }
            return sessionDocuments.map((sessionDocument: SessionDocument) => {
                return this.fromDocument(sessionDocument);
            });
        });
    }

    public fromDocument(sessionDocument: SessionDocument): Session {
        return new Session(sessionDocument.userId, sessionDocument.flow_duration_preference, sessionDocument.break_preference, sessionDocument.last_goal, sessionDocument.standard_picture, sessionDocument.pose_data, sessionDocument.tab_usage, sessionDocument.analysis, sessionDocument.sessionId);
    }

    public toDocument(session: Session): SessionDocument {
        return {
            sessionId: session.getSessionId(),
            userId: session.getUserId(),
            flow_duration_preference: session.getFlowDurationPreference(),
            break_preference: session.getBreakPreference(),
            last_goal: session.getLastGoal(),
            standard_picture: session.getStandardPicture(),
            pose_data: session.getPoseData(),
            tab_usage: session.getTabUsage(),
            analysis: session.getAnalysis()
        };
    }

    public async save(session: Session): Promise<boolean> {
        return this.sessionRepository.save(this.toDocument(session));
    }
}