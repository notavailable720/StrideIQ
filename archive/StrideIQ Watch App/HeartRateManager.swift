//
//  HeartRateManager.swift
//  StrideIQ
//
//  Created by Tony Huang on 4/16/26.
//
// HeartRateManager.swift
import Foundation
import HealthKit
import Combine
import WatchKit

@MainActor
final class HeartRateManager: NSObject, ObservableObject {
    @Published var currentHR: Double = 0
    @Published var isStreaming = false
    
    private let healthStore = HKHealthStore()
    private var session: HKWorkoutSession?
    private var builder: HKLiveWorkoutBuilder?
    
    // Identify this athlete. Later, replace with a configured ID.
    let athleteID: String = WKInterfaceDevice.current().name
    private let sender = HRSender()
    
    func requestAuth() async throws {
        let types: Set = [HKQuantityType.quantityType(forIdentifier: .heartRate)!]
        try await healthStore.requestAuthorization(toShare: [], read: types)
    }
    
    func start() throws {
        #if targetEnvironment(simulator)
        // Simulator: fake HR data in an async loop
        isStreaming = true
        Task { @MainActor [weak self] in
            while let self, self.isStreaming {
                let fakeHR = Double.random(in: 130...180)
                self.handleNewHR(fakeHR)
                try? await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
            }
        }
        #else
        // Real device: actual HealthKit workout session
        let config = HKWorkoutConfiguration()
        config.activityType = .running
        config.locationType = .outdoor
        
        let session = try HKWorkoutSession(healthStore: healthStore, configuration: config)
        let builder = session.associatedWorkoutBuilder()
        builder.dataSource = HKLiveWorkoutDataSource(healthStore: healthStore, workoutConfiguration: config)
        
        session.delegate = self
        builder.delegate = self
        
        self.session = session
        self.builder = builder
        
        let start = Date()
        session.startActivity(with: start)
        builder.beginCollection(withStart: start) { _, _ in }
        isStreaming = true
        #endif
    }
    
    func stop() {
        session?.end()
        isStreaming = false
    }
    
    fileprivate func handleNewHR(_ bpm: Double) {
        currentHR = bpm
        sender.send(athleteID: athleteID, hr: bpm, timestamp: Date())
    }
}

extension HeartRateManager: HKWorkoutSessionDelegate {
    nonisolated func workoutSession(_ workoutSession: HKWorkoutSession,
                                    didChangeTo toState: HKWorkoutSessionState,
                                    from fromState: HKWorkoutSessionState,
                                    date: Date) {}
    nonisolated func workoutSession(_ workoutSession: HKWorkoutSession, didFailWithError error: Error) {}
}

extension HeartRateManager: HKLiveWorkoutBuilderDelegate {
    nonisolated func workoutBuilderDidCollectEvent(_ workoutBuilder: HKLiveWorkoutBuilder) {}
    
    nonisolated func workoutBuilder(_ workoutBuilder: HKLiveWorkoutBuilder,
                                    didCollectDataOf collectedTypes: Set<HKSampleType>) {
        guard let hrType = HKQuantityType.quantityType(forIdentifier: .heartRate),
              collectedTypes.contains(hrType),
              let stats = workoutBuilder.statistics(for: hrType),
              let q = stats.mostRecentQuantity() else { return }
        let bpm = q.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
        Task { @MainActor in self.handleNewHR(bpm) }
    }
}
