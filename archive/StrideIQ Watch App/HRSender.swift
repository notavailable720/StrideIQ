//
//  HRSender.swift
//  StrideIQ
//
//  Created by Tony Huang on 4/16/26.
//

// HRSender.swift  — simple UDP broadcast to the coach laptop
import Foundation
import Network

final class HRSender {
    // For MVP: point at the coach laptop's IP on the shared Wi-Fi.
    // Easiest first version: hardcode it. Later, use Bonjour/NWBrowser to discover.
    private let host: NWEndpoint.Host = "10.136.177.235"
    private let port: NWEndpoint.Port = 9999
    private lazy var connection: NWConnection = {
        let c = NWConnection(host: host, port: port, using: .udp)
        c.start(queue: .global(qos: .utility))
        return c
    }()
    
    func send(athleteID: String, hr: Double, timestamp: Date) {
        let payload: [String: Any] = [
            "athlete_id": athleteID,
            "hr": hr,
            "ts": timestamp.timeIntervalSince1970
        ]
        guard let data = try? JSONSerialization.data(withJSONObject: payload) else { return }
        connection.send(content: data, completion: .idempotent)
    }
}
