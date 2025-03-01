import { Collection, Filter } from "mongodb";
import { SessionDocument } from "../models/SessionDocument";


export class SessionRepository {
    private collection: Collection<SessionDocument>;

    constructor(collection: Collection<SessionDocument>) {
        this.collection = collection;
    }

    /**
     * Get function - Retrieves a session by sessionId.
     */
    public async getSessionBySessionId(sessionId: string): Promise<SessionDocument | null> {
        return await this.collection.findOne({ "sessionId": sessionId }, { projection: { _id: 0 } });
    }

    /**
     * Get function - retrieves all sessions by userId.
     */
    public async getSessionByUserId(userId: string): Promise<SessionDocument[] | null> {
        return await this.collection.find({ "userId": userId }, { projection: { _id: 0 } }).toArray();
    }

    /**
     * Save function - Update a session or insert a new one.
     */
    public async save(sessionDocument: SessionDocument): Promise<boolean> {

        const query: Filter<SessionDocument> = { sessionId: sessionDocument.sessionId };
        const update = { $set: Object.assign({}, sessionDocument) };
        const options = { upsert: true };
        const result = await this.collection.updateOne(query, update, options);
        return result.acknowledged;
    }
}