import { Session } from "../models/Session";
import { SessionDocument } from "../models/SessionDocument";

export interface SessionService {

    getSessionBySessionId(sessionId: string): Promise<Session | null>;

    getSessionByUserId(userId: string): Promise<Session[]>;

    fromDocument(sessionDocument: SessionDocument): Session;

    toDocument(session: Session): SessionDocument;

    save(session: Session): Promise<boolean>;
}